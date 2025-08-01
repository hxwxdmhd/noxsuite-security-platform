/**
 * Plugin Manager Component - Visual Plugin Management Interface
 * Features: Plugin discovery, installation, configuration, ADHD-friendly design
 * @author @hxwxdmhd
 * @version 1.0.0
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Typography,
  Button,
  IconButton,
  Chip,
  Avatar,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab,
  Badge,
  Tooltip,
  Alert,
  Snackbar,
  CircularProgress,
  Rating,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Extension as ExtensionIcon,
  GetApp as DownloadIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Check as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Palette as PaletteIcon,
  Build as BuildIcon,
  Public as PublicIcon,
  Storage as StorageIcon,
  CloudDownload as CloudDownloadIcon,
  Folder as FolderIcon,
  Launch as LaunchIcon
} from '@mui/icons-material';

import { useAccessibility } from '../contexts/AccessibilityContext';
import { useSocket } from '../contexts/SocketContext';

const PluginManager = () => {
  const {
    theme,
    reducedMotion,
    highContrast,
    focusIndicators,
    cognitiveLoad,
    announceToScreenReader
  } = useAccessibility();
  
  const {
    isConnected,
    emit,
    subscribe
  } = useSocket();
  
  // Local state
  const [activeTab, setActiveTab] = useState(0);
  const [installedPlugins, setInstalledPlugins] = useState([]);
  const [availablePlugins, setAvailablePlugins] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [selectedPlugin, setSelectedPlugin] = useState(null);
  const [installing, setInstalling] = useState(new Set());
  const [configuring, setConfiguring] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [pluginConfigs, setPluginConfigs] = useState({});
  const [refreshing, setRefreshing] = useState(false);

  // Plugin categories
  const categories = [
    { value: 'all', label: 'All Categories', icon: <ExtensionIcon /> },
    { value: 'security', label: 'Security', icon: <SecurityIcon /> },
    { value: 'performance', label: 'Performance', icon: <SpeedIcon /> },
    { value: 'ui', label: 'User Interface', icon: <PaletteIcon /> },
    { value: 'development', label: 'Development', icon: <BuildIcon /> },
    { value: 'network', label: 'Network', icon: <PublicIcon /> },
    { value: 'storage', label: 'Storage', icon: <StorageIcon /> }
  ];

  // Tab configuration
  const tabs = [
    { label: 'Installed', icon: <ExtensionIcon /> },
    { label: 'Available', icon: <CloudDownloadIcon /> },
    { label: 'Settings', icon: <SettingsIcon /> }
  ];

  // Mock data for available plugins
  const mockAvailablePlugins = [
    {
      id: 'enhanced-scanner',
      name: 'Enhanced Security Scanner',
      version: '2.1.0',
      author: 'NoxSuite Team',
      description: 'Advanced vulnerability scanner with machine learning detection capabilities.',
      category: 'security',
      rating: 4.8,
      downloads: 15420,
      price: 'Free',
      features: ['ML-based detection', 'Custom rules', 'API integration', 'Real-time scanning'],
      screenshots: ['/api/placeholder/400/250'],
      compatibility: ['NoxSuite 11.0+'],
      lastUpdated: '2024-01-15',
      size: '12.5 MB',
      dependencies: ['python>=3.8', 'tensorflow>=2.0']
    },
    {
      id: 'ui-accessibility',
      name: 'Accessibility Enhancer',
      version: '1.5.3',
      author: 'Community',
      description: 'Comprehensive accessibility improvements for users with disabilities.',
      category: 'ui',
      rating: 4.9,
      downloads: 8750,
      price: 'Free',
      features: ['WCAG 2.1 AA compliance', 'Screen reader support', 'High contrast modes', 'Keyboard navigation'],
      screenshots: ['/api/placeholder/400/250'],
      compatibility: ['NoxSuite 10.0+'],
      lastUpdated: '2024-01-10',
      size: '3.2 MB',
      dependencies: ['react>=18.0']
    },
    {
      id: 'performance-optimizer',
      name: 'Performance Optimizer Pro',
      version: '3.0.1',
      author: 'TechFlow Solutions',
      description: 'Optimize system performance with advanced algorithms and caching.',
      category: 'performance',
      rating: 4.6,
      downloads: 22100,
      price: '$29.99',
      features: ['Smart caching', 'Resource optimization', 'Performance analytics', 'Auto-scaling'],
      screenshots: ['/api/placeholder/400/250'],
      compatibility: ['NoxSuite 11.0+'],
      lastUpdated: '2024-01-12',
      size: '18.7 MB',
      dependencies: ['redis>=6.0', 'nginx>=1.20']
    }
  ];

  // Subscribe to plugin events
  useEffect(() => {
    const unsubscribeInstalled = subscribe('plugins_updated', (plugins) => {
      setInstalledPlugins(plugins);
    });
    
    const unsubscribeAvailable = subscribe('available_plugins_updated', (plugins) => {
      setAvailablePlugins(plugins);
    });
    
    const unsubscribeConfigs = subscribe('plugin_configs_updated', (configs) => {
      setPluginConfigs(configs);
    });

    // Initialize with mock data
    setAvailablePlugins(mockAvailablePlugins);
    
    // Request current plugin data
    if (isConnected) {
      emit('get_installed_plugins');
      emit('get_available_plugins');
      emit('get_plugin_configs');
    }

    return () => {
      unsubscribeInstalled();
      unsubscribeAvailable();
      unsubscribeConfigs();
    };
  }, [subscribe, emit, isConnected]);

  // Filter plugins based on search and category
  const filteredAvailablePlugins = useMemo(() => {
    let filtered = availablePlugins;
    
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(plugin => plugin.category === categoryFilter);
    }
    
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(plugin =>
        plugin.name.toLowerCase().includes(search) ||
        plugin.description.toLowerCase().includes(search) ||
        plugin.author.toLowerCase().includes(search)
      );
    }
    
    return filtered;
  }, [availablePlugins, categoryFilter, searchTerm]);

  const filteredInstalledPlugins = useMemo(() => {
    let filtered = installedPlugins;
    
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(plugin =>
        plugin.name.toLowerCase().includes(search) ||
        plugin.description.toLowerCase().includes(search)
      );
    }
    
    return filtered;
  }, [installedPlugins, searchTerm]);

  // Get category icon
  const getCategoryIcon = useCallback((category) => {
    const categoryData = categories.find(cat => cat.value === category);
    return categoryData ? categoryData.icon : <ExtensionIcon />;
  }, []);

  // Install plugin
  const handleInstallPlugin = useCallback(async (plugin) => {
    setInstalling(prev => new Set(prev).add(plugin.id));
    announceToScreenReader(`Installing plugin ${plugin.name}`);
    
    try {
      emit('install_plugin', {
        id: plugin.id,
        name: plugin.name,
        version: plugin.version
      });
      
      // Simulate installation time
      setTimeout(() => {
        setInstalling(prev => {
          const newSet = new Set(prev);
          newSet.delete(plugin.id);
          return newSet;
        });
        
        setSnackbar({
          open: true,
          message: `${plugin.name} installed successfully`,
          severity: 'success'
        });
        
        announceToScreenReader(`Plugin ${plugin.name} installed successfully`);
      }, 3000);
      
    } catch (error) {
      console.error('Failed to install plugin:', error);
      setInstalling(prev => {
        const newSet = new Set(prev);
        newSet.delete(plugin.id);
        return newSet;
      });
      
      setSnackbar({
        open: true,
        message: `Failed to install ${plugin.name}`,
        severity: 'error'
      });
    }
  }, [emit, announceToScreenReader]);

  // Uninstall plugin
  const handleUninstallPlugin = useCallback(async (plugin) => {
    announceToScreenReader(`Uninstalling plugin ${plugin.name}`);
    
    try {
      emit('uninstall_plugin', { id: plugin.id });
      
      setSnackbar({
        open: true,
        message: `${plugin.name} uninstalled successfully`,
        severity: 'success'
      });
      
      announceToScreenReader(`Plugin ${plugin.name} uninstalled successfully`);
      
    } catch (error) {
      console.error('Failed to uninstall plugin:', error);
      setSnackbar({
        open: true,
        message: `Failed to uninstall ${plugin.name}`,
        severity: 'error'
      });
    }
  }, [emit, announceToScreenReader]);

  // Configure plugin
  const handleConfigurePlugin = useCallback((plugin) => {
    setConfiguring(plugin);
  }, []);

  // Close plugin details
  const handleClosePluginDetails = useCallback(() => {
    setSelectedPlugin(null);
  }, []);

  // Close configuration dialog
  const handleCloseConfiguration = useCallback(() => {
    setConfiguring(null);
  }, []);

  // Refresh plugin list
  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    announceToScreenReader('Refreshing plugin list');
    
    emit('refresh_plugins');
    
    setTimeout(() => {
      setRefreshing(false);
      announceToScreenReader('Plugin list refreshed');
    }, 1000);
  }, [emit, announceToScreenReader]);

  // Plugin Card Component
  const PluginCard = ({ plugin, isInstalled = false }) => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: theme.cardBackground,
        border: highContrast ? `2px solid ${theme.primary}` : 'none',
        transition: reducedMotion.enabled ? 'none' : 'transform 0.2s, box-shadow 0.2s',
        '&:hover': reducedMotion.enabled ? {} : {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 24px ${theme.shadow}`
        }
      }}
    >
      {plugin.screenshots && plugin.screenshots[0] && (
        <CardMedia
          component="img"
          height="140"
          image={plugin.screenshots[0]}
          alt={`${plugin.name} screenshot`}
          sx={{
            objectFit: 'cover'
          }}
        />
      )}
      
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Avatar
            sx={{
              bgcolor: theme.primary,
              width: 32,
              height: 32,
              mr: 1
            }}
          >
            {getCategoryIcon(plugin.category)}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography
              variant="h6"
              component="h3"
              sx={{
                fontSize: cognitiveLoad.simplified ? '1.1rem' : '1.25rem',
                fontWeight: 600
              }}
            >
              {plugin.name}
            </Typography>
            <Typography
              variant="caption"
              sx={{ color: theme.textSecondary }}
            >
              by {plugin.author} • v{plugin.version}
            </Typography>
          </Box>
          
          {plugin.price && plugin.price !== 'Free' && (
            <Chip
              label={plugin.price}
              color="primary"
              size="small"
            />
          )}
        </Box>
        
        <Typography
          variant="body2"
          sx={{
            color: theme.textSecondary,
            mb: 2,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical'
          }}
        >
          {plugin.description}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Chip
            icon={getCategoryIcon(plugin.category)}
            label={plugin.category}
            size="small"
            variant="outlined"
          />
          
          {plugin.rating && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Rating
                value={plugin.rating}
                readOnly
                size="small"
                precision={0.1}
              />
              <Typography variant="caption" sx={{ color: theme.textSecondary }}>
                ({plugin.rating})
              </Typography>
            </Box>
          )}
        </Box>
        
        {plugin.downloads && (
          <Typography variant="caption" sx={{ color: theme.textSecondary }}>
            {plugin.downloads.toLocaleString()} downloads
          </Typography>
        )}
      </CardContent>
      
      <CardActions sx={{ p: 2, pt: 0 }}>
        <Button
          size="small"
          onClick={() => setSelectedPlugin(plugin)}
          sx={{
            '&:focus': focusIndicators.enabled ? {
              outline: `2px solid ${theme.primary}`,
              outlineOffset: '2px'
            } : {}
          }}
        >
          <InfoIcon sx={{ mr: 0.5 }} />
          Details
        </Button>
        
        {isInstalled ? (
          <>
            <Button
              size="small"
              onClick={() => handleConfigurePlugin(plugin)}
              sx={{
                '&:focus': focusIndicators.enabled ? {
                  outline: `2px solid ${theme.primary}`,
                  outlineOffset: '2px'
                } : {}
              }}
            >
              <SettingsIcon sx={{ mr: 0.5 }} />
              Configure
            </Button>
            <Button
              size="small"
              color="error"
              onClick={() => handleUninstallPlugin(plugin)}
              sx={{
                '&:focus': focusIndicators.enabled ? {
                  outline: `2px solid ${theme.primary}`,
                  outlineOffset: '2px'
                } : {}
              }}
            >
              <DeleteIcon sx={{ mr: 0.5 }} />
              Remove
            </Button>
          </>
        ) : (
          <Button
            size="small"
            variant="contained"
            disabled={installing.has(plugin.id) || !isConnected}
            onClick={() => handleInstallPlugin(plugin)}
            sx={{
              backgroundColor: theme.primary,
              '&:focus': focusIndicators.enabled ? {
                outline: `2px solid ${theme.primary}`,
                outlineOffset: '2px'
              } : {}
            }}
          >
            {installing.has(plugin.id) ? (
              <CircularProgress size={16} sx={{ mr: 0.5 }} />
            ) : (
              <DownloadIcon sx={{ mr: 0.5 }} />
            )}
            {installing.has(plugin.id) ? 'Installing...' : 'Install'}
          </Button>
        )}
      </CardActions>
    </Card>
  );

  return (
    <Box
      sx={{
        p: { xs: 1, sm: 2, md: 3 },
        minHeight: '100vh',
        backgroundColor: theme.background,
        color: theme.text
      }}
      role="main"
      aria-label="Plugin Manager"
    >
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="h4"
          component="h1"
          sx={{
            fontWeight: 600,
            color: theme.primary,
            fontSize: cognitiveLoad.simplified ? '2rem' : '2.5rem',
            mb: 1
          }}
        >
          🧩 Plugin Manager
        </Typography>
        <Typography
          variant="subtitle1"
          sx={{
            color: theme.textSecondary,
            fontSize: cognitiveLoad.simplified ? '1rem' : '1.1rem'
          }}
        >
          Discover, install, and manage NoxSuite plugins
        </Typography>
      </Box>

      {/* Connection Status */}
      {!isConnected && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Plugin management offline. Limited functionality available.
        </Alert>
      )}

      {/* Controls */}
      <Card
        sx={{
          mb: 3,
          backgroundColor: theme.cardBackground,
          border: highContrast ? `2px solid ${theme.primary}` : 'none'
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <TextField
              label="Search plugins"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: theme.textSecondary }} />
              }}
              sx={{ minWidth: 250 }}
            />
            
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Category</InputLabel>
              <Select
                value={categoryFilter}
                label="Category"
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                {categories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {category.icon}
                      {category.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Button
              variant="outlined"
              startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
              onClick={handleRefresh}
              disabled={refreshing || !isConnected}
              sx={{
                borderColor: theme.primary,
                color: theme.primary,
                '&:focus': focusIndicators.enabled ? {
                  outline: `2px solid ${theme.primary}`,
                  outlineOffset: '2px'
                } : {}
              }}
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card
        sx={{
          backgroundColor: theme.cardBackground,
          border: highContrast ? `2px solid ${theme.primary}` : 'none'
        }}
      >
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
          sx={{
            borderBottom: `1px solid ${theme.divider}`,
            '& .MuiTab-root': {
              color: theme.textSecondary,
              '&.Mui-selected': {
                color: theme.primary
              },
              '&:focus': focusIndicators.enabled ? {
                outline: `2px solid ${theme.primary}`,
                outlineOffset: '2px'
              } : {}
            }
          }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              label={tab.label}
              icon={tab.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>

        <Box sx={{ p: 3 }}>
          {/* Installed Plugins Tab */}
          {activeTab === 0 && (
            <Grid container spacing={3}>
              {filteredInstalledPlugins.length === 0 ? (
                <Grid item xs={12}>
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      py: 8,
                      color: theme.textSecondary
                    }}
                  >
                    <ExtensionIcon sx={{ fontSize: 64, mb: 2 }} />
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      No plugins installed
                    </Typography>
                    <Typography variant="body2">
                      Browse available plugins to enhance your NoxSuite experience
                    </Typography>
                    <Button
                      variant="contained"
                      sx={{ mt: 2, backgroundColor: theme.primary }}
                      onClick={() => setActiveTab(1)}
                    >
                      Browse Plugins
                    </Button>
                  </Box>
                </Grid>
              ) : (
                filteredInstalledPlugins.map((plugin) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={plugin.id}>
                    <PluginCard plugin={plugin} isInstalled={true} />
                  </Grid>
                ))
              )}
            </Grid>
          )}

          {/* Available Plugins Tab */}
          {activeTab === 1 && (
            <Grid container spacing={3}>
              {filteredAvailablePlugins.map((plugin) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={plugin.id}>
                  <PluginCard plugin={plugin} isInstalled={false} />
                </Grid>
              ))}
              
              {filteredAvailablePlugins.length === 0 && (
                <Grid item xs={12}>
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      py: 8,
                      color: theme.textSecondary
                    }}
                  >
                    <SearchIcon sx={{ fontSize: 64, mb: 2 }} />
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      No plugins found
                    </Typography>
                    <Typography variant="body2">
                      Try adjusting your search terms or category filter
                    </Typography>
                  </Box>
                </Grid>
              )}
            </Grid>
          )}

          {/* Settings Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 3 }}>
                Plugin Settings
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card
                    sx={{
                      backgroundColor: theme.background,
                      border: highContrast ? `1px solid ${theme.primary}` : 'none'
                    }}
                  >
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        Auto-Update Settings
                      </Typography>
                      
                      <FormControlLabel
                        control={<Switch defaultChecked color="primary" />}
                        label="Enable automatic plugin updates"
                        sx={{ mb: 2 }}
                      />
                      
                      <FormControlLabel
                        control={<Switch color="primary" />}
                        label="Update plugins in background"
                        sx={{ mb: 2 }}
                      />
                      
                      <FormControlLabel
                        control={<Switch defaultChecked color="primary" />}
                        label="Notify before major updates"
                      />
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card
                    sx={{
                      backgroundColor: theme.background,
                      border: highContrast ? `1px solid ${theme.primary}` : 'none'
                    }}
                  >
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        Security Settings
                      </Typography>
                      
                      <FormControlLabel
                        control={<Switch defaultChecked color="primary" />}
                        label="Verify plugin signatures"
                        sx={{ mb: 2 }}
                      />
                      
                      <FormControlLabel
                        control={<Switch defaultChecked color="primary" />}
                        label="Scan plugins for malware"
                        sx={{ mb: 2 }}
                      />
                      
                      <FormControlLabel
                        control={<Switch color="primary" />}
                        label="Allow beta plugins"
                      />
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </Box>
      </Card>

      {/* Plugin Details Dialog */}
      <Dialog
        open={!!selectedPlugin}
        onClose={handleClosePluginDetails}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: theme.cardBackground,
            border: highContrast ? `2px solid ${theme.primary}` : 'none'
          }
        }}
      >
        {selectedPlugin && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: theme.primary }}>
                  {getCategoryIcon(selectedPlugin.category)}
                </Avatar>
                <Box>
                  <Typography variant="h6">
                    {selectedPlugin.name}
                  </Typography>
                  <Typography variant="subtitle2" sx={{ color: theme.textSecondary }}>
                    v{selectedPlugin.version} by {selectedPlugin.author}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            
            <DialogContent>
              <Typography variant="body1" sx={{ mb: 3 }}>
                {selectedPlugin.description}
              </Typography>
              
              {selectedPlugin.features && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    Features
                  </Typography>
                  <List dense>
                    {selectedPlugin.features.map((feature, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText primary={feature} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" sx={{ color: theme.textSecondary }}>
                    Category
                  </Typography>
                  <Typography>{selectedPlugin.category}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" sx={{ color: theme.textSecondary }}>
                    Size
                  </Typography>
                  <Typography>{selectedPlugin.size}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" sx={{ color: theme.textSecondary }}>
                    Last Updated
                  </Typography>
                  <Typography>
                    {new Date(selectedPlugin.lastUpdated).toLocaleDateString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" sx={{ color: theme.textSecondary }}>
                    Downloads
                  </Typography>
                  <Typography>
                    {selectedPlugin.downloads?.toLocaleString() || 'N/A'}
                  </Typography>
                </Grid>
              </Grid>
            </DialogContent>
            
            <DialogActions>
              <Button onClick={handleClosePluginDetails}>
                Close
              </Button>
              <Button
                variant="contained"
                onClick={() => {
                  handleInstallPlugin(selectedPlugin);
                  handleClosePluginDetails();
                }}
                disabled={installing.has(selectedPlugin.id) || !isConnected}
                sx={{ backgroundColor: theme.primary }}
              >
                Install Plugin
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default PluginManager;
