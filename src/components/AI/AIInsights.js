import React, { useState, useEffect, useContext } from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    Card,
    CardContent,
    CardHeader,
    Alert,
    Button,
    LinearProgress,
    Chip,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Avatar,
    Tooltip,
    Badge,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    useTheme
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    Security as SecurityIcon,
    Speed as SpeedIcon,
    Person as PersonIcon,
    TrendingUp as TrendingUpIcon,
    Warning as WarningIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Info as InfoIcon,
    Refresh as RefreshIcon,
    Assessment as AssessmentIcon,
    Psychology as PsychologyIcon,
    AutoFixHigh as AutoFixHighIcon,
    Shield as ShieldIcon,
    Analytics as AnalyticsIcon,
    Visibility as VisibilityIcon,
    VisibilityOff as VisibilityOffIcon
} from '@mui/icons-material';
import { Line, Doughnut, Bar, Radar } from 'react-chartjs-2';
import { AccessibilityContext } from '../../contexts/AccessibilityContext';
import { PerformanceContext } from '../../contexts/PerformanceContext';
import { api } from '../../utils/api';

const AIInsights = () => {
    const theme = useTheme();
    const { settings } = useContext(AccessibilityContext);
    const { optimizations } = useContext(PerformanceContext);
    
    // State management
    const [aiStatus, setAiStatus] = useState({});
    const [threatAnalysis, setThreatAnalysis] = useState(null);
    const [performanceOptimization, setPerformanceOptimization] = useState(null);
    const [userBehaviorInsights, setUserBehaviorInsights] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds
    const [detailsDialog, setDetailsDialog] = useState({ open: false, type: null, data: null });
    const [threatHistory, setThreatHistory] = useState([]);
    const [performanceHistory, setPerformanceHistory] = useState([]);

    // Load AI status and capabilities
    const loadAIStatus = async () => {
        try {
            const response = await api.get('/ai/status');
            setAiStatus(response.data);
        } catch (err) {
            console.error('Failed to load AI status:', err);
            setError('Failed to load AI status');
        }
    };

    // Analyze current threats
    const analyzeThreat = async () => {
        try {
            const threatData = {
                source_ip: window.location.hostname,
                user_agent: navigator.userAgent,
                request_frequency: 1,
                payload_size: 1024,
                response_time: performance.now(),
                error_count: 0,
                unique_endpoints: 5,
                geographic_distance: 0,
                session_duration: Date.now() - sessionStorage.getItem('sessionStart') || 0
            };

            const response = await api.post('/ai/analyze_threat', threatData);
            setThreatAnalysis(response.data);
            
            // Add to history
            setThreatHistory(prev => [
                { ...response.data, timestamp: new Date().toISOString() },
                ...prev.slice(0, 9) // Keep last 10 entries
            ]);
        } catch (err) {
            console.error('Failed to analyze threat:', err);
        }
    };

    // Optimize performance
    const optimizePerformance = async () => {
        try {
            const performanceData = {
                metrics: {
                    cpu_usage: Math.random() * 100,
                    memory_usage: Math.random() * 100,
                    response_time: performance.now(),
                    error_rate: Math.random() * 5
                }
            };

            const response = await api.post('/ai/optimize_performance', performanceData);
            setPerformanceOptimization(response.data);
            
            // Add to history
            setPerformanceHistory(prev => [
                { ...response.data, timestamp: new Date().toISOString() },
                ...prev.slice(0, 9) // Keep last 10 entries
            ]);
        } catch (err) {
            console.error('Failed to optimize performance:', err);
        }
    };

    // Analyze user behavior
    const analyzeUserBehavior = async () => {
        try {
            const behaviorData = {
                user_id: 'current_user',
                behavior_data: {
                    session_duration: Date.now() - (sessionStorage.getItem('sessionStart') || Date.now()),
                    click_frequency: Math.random() * 5,
                    page_views: parseInt(sessionStorage.getItem('pageViews') || '1'),
                    features_used: ['dashboard', 'security', 'ai_insights'],
                    error_encounters: parseInt(sessionStorage.getItem('errorCount') || '0'),
                    help_requests: parseInt(sessionStorage.getItem('helpRequests') || '0'),
                    accessibility_features_used: Object.values(settings).filter(Boolean).length,
                    response_time_variance: Math.random() * 200,
                    zoom_level: parseInt(getComputedStyle(document.documentElement).fontSize) || 100,
                    mouse_usage: 80
                }
            };

            const response = await api.post('/ai/analyze_user_behavior', behaviorData);
            setUserBehaviorInsights(response.data);
        } catch (err) {
            console.error('Failed to analyze user behavior:', err);
        }
    };

    // Load all AI insights
    const loadAllInsights = async () => {
        setLoading(true);
        setError(null);
        
        try {
            await Promise.all([
                loadAIStatus(),
                analyzeThreat(),
                optimizePerformance(),
                analyzeUserBehavior()
            ]);
        } catch (err) {
            setError('Failed to load AI insights');
        } finally {
            setLoading(false);
        }
    };

    // Auto-refresh effect
    useEffect(() => {
        loadAllInsights();
        
        if (autoRefresh) {
            const interval = setInterval(loadAllInsights, refreshInterval);
            return () => clearInterval(interval);
        }
    }, [autoRefresh, refreshInterval]);

    // Initialize session tracking
    useEffect(() => {
        if (!sessionStorage.getItem('sessionStart')) {
            sessionStorage.setItem('sessionStart', Date.now().toString());
        }
        
        const currentPageViews = parseInt(sessionStorage.getItem('pageViews') || '0');
        sessionStorage.setItem('pageViews', (currentPageViews + 1).toString());
    }, []);

    // Keyboard navigation
    useEffect(() => {
        const handleKeyDown = (event) => {
            if (event.altKey) {
                switch (event.key) {
                    case 'r':
                        event.preventDefault();
                        loadAllInsights();
                        break;
                    case 't':
                        event.preventDefault();
                        setDetailsDialog({ open: true, type: 'threat', data: threatAnalysis });
                        break;
                    case 'p':
                        event.preventDefault();
                        setDetailsDialog({ open: true, type: 'performance', data: performanceOptimization });
                        break;
                    case 'u':
                        event.preventDefault();
                        setDetailsDialog({ open: true, type: 'behavior', data: userBehaviorInsights });
                        break;
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [threatAnalysis, performanceOptimization, userBehaviorInsights]);

    // Get threat severity color
    const getThreatSeverityColor = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical': return theme.palette.error.main;
            case 'high': return theme.palette.warning.main;
            case 'medium': return theme.palette.info.main;
            case 'low': return theme.palette.success.main;
            default: return theme.palette.grey[500];
        }
    };

    // Get threat severity icon
    const getThreatSeverityIcon = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical': return <ErrorIcon />;
            case 'high': return <WarningIcon />;
            case 'medium': return <InfoIcon />;
            case 'low': return <CheckCircleIcon />;
            default: return <SecurityIcon />;
        }
    };

    // Chart configurations
    const threatTrendData = {
        labels: threatHistory.map((_, index) => `T-${index * 30}s`),
        datasets: [{
            label: 'Threat Confidence',
            data: threatHistory.map(t => t.confidence * 100),
            borderColor: theme.palette.error.main,
            backgroundColor: theme.palette.error.light,
            fill: true,
            tension: 0.4
        }]
    };

    const performanceTrendData = {
        labels: performanceHistory.map((_, index) => `T-${index * 30}s`),
        datasets: [{
            label: 'Performance Improvement %',
            data: performanceHistory.map(p => p.improvement_percentage || 0),
            borderColor: theme.palette.success.main,
            backgroundColor: theme.palette.success.light,
            fill: true,
            tension: 0.4
        }]
    };

    const aiCapabilitiesData = {
        labels: ['Threat Detection', 'Performance Optimization', 'Behavior Analysis', 'Anomaly Detection', 'Real-time Learning'],
        datasets: [{
            label: 'AI Capability Score',
            data: [85, 92, 78, 88, 75],
            backgroundColor: [
                theme.palette.error.light,
                theme.palette.success.light,
                theme.palette.info.light,
                theme.palette.warning.light,
                theme.palette.primary.light
            ],
            borderColor: [
                theme.palette.error.main,
                theme.palette.success.main,
                theme.palette.info.main,
                theme.palette.warning.main,
                theme.palette.primary.main
            ],
            borderWidth: 2
        }]
    };

    // Show details dialog
    const showDetails = (type, data) => {
        setDetailsDialog({ open: true, type, data });
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading AI Insights...</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center' }}>
                    <PsychologyIcon sx={{ mr: 2, fontSize: 40 }} />
                    AI Insights Dashboard
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Refresh AI Insights (Alt+R)">
                        <IconButton 
                            onClick={loadAllInsights} 
                            color="primary"
                            aria-label="Refresh AI insights"
                        >
                            <RefreshIcon />
                        </IconButton>
                    </Tooltip>
                    
                    <Tooltip title={autoRefresh ? 'Disable Auto-refresh' : 'Enable Auto-refresh'}>
                        <IconButton 
                            onClick={() => setAutoRefresh(!autoRefresh)}
                            color={autoRefresh ? 'primary' : 'default'}
                            aria-label={autoRefresh ? 'Disable auto-refresh' : 'Enable auto-refresh'}
                        >
                            {autoRefresh ? <VisibilityIcon /> : <VisibilityOffIcon />}
                        </IconButton>
                    </Tooltip>
                </Box>
            </Box>

            {/* Keyboard Shortcuts Help */}
            {settings.showKeyboardShortcuts && (
                <Alert severity="info" sx={{ mb: 3 }}>
                    <Typography variant="body2">
                        <strong>Keyboard Shortcuts:</strong> Alt+R (Refresh), Alt+T (Threat Details), 
                        Alt+P (Performance Details), Alt+U (User Behavior Details)
                    </Typography>
                </Alert>
            )}

            {/* Error Alert */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* AI Status Overview */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6} lg={3}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
                                    <AssessmentIcon />
                                </Avatar>
                                <Typography variant="h6">AI Engine Status</Typography>
                            </Box>
                            <Typography variant="h4" color="primary">
                                {aiStatus.ai_engine_status === 'operational' ? 'Online' : 'Offline'}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                {aiStatus.models_loaded || 0} models loaded
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6} lg={3}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: getThreatSeverityColor(threatAnalysis?.severity), mr: 2 }}>
                                    {getThreatSeverityIcon(threatAnalysis?.severity)}
                                </Avatar>
                                <Typography variant="h6">Threat Level</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ color: getThreatSeverityColor(threatAnalysis?.severity) }}>
                                {threatAnalysis?.severity || 'Low'}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                {threatAnalysis?.confidence ? `${(threatAnalysis.confidence * 100).toFixed(1)}% confidence` : 'No threats detected'}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6} lg={3}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: theme.palette.success.main, mr: 2 }}>
                                    <SpeedIcon />
                                </Avatar>
                                <Typography variant="h6">Performance</Typography>
                            </Box>
                            <Typography variant="h4" color="success.main">
                                {performanceOptimization?.improvement_percentage ? 
                                    `+${performanceOptimization.improvement_percentage.toFixed(1)}%` : 
                                    'Optimized'
                                }
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                {performanceOptimization?.component || 'System performance'}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6} lg={3}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: theme.palette.info.main, mr: 2 }}>
                                    <PersonIcon />
                                </Avatar>
                                <Typography variant="h6">User Behavior</Typography>
                            </Box>
                            <Typography variant="h4" color="info.main">
                                {userBehaviorInsights?.behavior_pattern || 'Normal'}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                {userBehaviorInsights?.anomaly_score ? 
                                    `${(userBehaviorInsights.anomaly_score * 100).toFixed(1)}% anomaly` : 
                                    'Typical usage pattern'
                                }
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Detailed Analysis Sections */}
            <Grid container spacing={3}>
                {/* Threat Analysis */}
                <Grid item xs={12} lg={4}>
                    <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                                <ShieldIcon sx={{ mr: 1 }} />
                                Threat Analysis
                                <Tooltip title="View threat details (Alt+T)">
                                    <IconButton 
                                        size="small" 
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            showDetails('threat', threatAnalysis);
                                        }}
                                        sx={{ ml: 1 }}
                                    >
                                        <VisibilityIcon fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                            </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {threatAnalysis ? (
                                <Box>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>Threat Type:</strong> {threatAnalysis.threat_type}
                                    </Typography>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>Description:</strong> {threatAnalysis.description}
                                    </Typography>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>Recommended Action:</strong> {threatAnalysis.recommended_action}
                                    </Typography>
                                    
                                    <Box sx={{ mt: 2 }}>
                                        <Typography variant="body2" gutterBottom>
                                            Confidence Level
                                        </Typography>
                                        <LinearProgress 
                                            variant="determinate" 
                                            value={threatAnalysis.confidence * 100}
                                            sx={{ height: 8, borderRadius: 4 }}
                                        />
                                        <Typography variant="caption" color="textSecondary">
                                            {(threatAnalysis.confidence * 100).toFixed(1)}%
                                        </Typography>
                                    </Box>

                                    {threatHistory.length > 0 && (
                                        <Box sx={{ mt: 2, height: 200 }}>
                                            <Typography variant="body2" gutterBottom>
                                                Threat Trend (Last 10 scans)
                                            </Typography>
                                            <Line 
                                                data={threatTrendData}
                                                options={{
                                                    responsive: true,
                                                    maintainAspectRatio: false,
                                                    scales: {
                                                        y: {
                                                            beginAtZero: true,
                                                            max: 100
                                                        }
                                                    }
                                                }}
                                            />
                                        </Box>
                                    )}
                                </Box>
                            ) : (
                                <Typography variant="body2" color="textSecondary">
                                    No threat analysis available
                                </Typography>
                            )}
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                {/* Performance Optimization */}
                <Grid item xs={12} lg={4}>
                    <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                                <AutoFixHighIcon sx={{ mr: 1 }} />
                                Performance Optimization
                                <Tooltip title="View performance details (Alt+P)">
                                    <IconButton 
                                        size="small" 
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            showDetails('performance', performanceOptimization);
                                        }}
                                        sx={{ ml: 1 }}
                                    >
                                        <VisibilityIcon fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                            </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {performanceOptimization ? (
                                <Box>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>Component:</strong> {performanceOptimization.component}
                                    </Typography>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>Strategy:</strong> {performanceOptimization.optimization_strategy}
                                    </Typography>
                                    
                                    <Box sx={{ mt: 2 }}>
                                        <Typography variant="body2" gutterBottom>
                                            Performance Improvement
                                        </Typography>
                                        <LinearProgress 
                                            variant="determinate" 
                                            value={Math.min(performanceOptimization.improvement_percentage || 0, 100)}
                                            color="success"
                                            sx={{ height: 8, borderRadius: 4 }}
                                        />
                                        <Typography variant="caption" color="textSecondary">
                                            +{(performanceOptimization.improvement_percentage || 0).toFixed(1)}%
                                        </Typography>
                                    </Box>

                                    {performanceOptimization.implementation_steps && (
                                        <Box sx={{ mt: 2 }}>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Implementation Steps:</strong>
                                            </Typography>
                                            <List dense>
                                                {performanceOptimization.implementation_steps.map((step, index) => (
                                                    <ListItem key={index} sx={{ pl: 0 }}>
                                                        <ListItemIcon>
                                                            <CheckCircleIcon fontSize="small" color="success" />
                                                        </ListItemIcon>
                                                        <ListItemText 
                                                            primary={step}
                                                            primaryTypographyProps={{ variant: 'body2' }}
                                                        />
                                                    </ListItem>
                                                ))}
                                            </List>
                                        </Box>
                                    )}

                                    {performanceHistory.length > 0 && (
                                        <Box sx={{ mt: 2, height: 200 }}>
                                            <Typography variant="body2" gutterBottom>
                                                Performance Trend
                                            </Typography>
                                            <Line 
                                                data={performanceTrendData}
                                                options={{
                                                    responsive: true,
                                                    maintainAspectRatio: false,
                                                    scales: {
                                                        y: {
                                                            beginAtZero: true
                                                        }
                                                    }
                                                }}
                                            />
                                        </Box>
                                    )}
                                </Box>
                            ) : (
                                <Typography variant="body2" color="textSecondary">
                                    No performance optimization available
                                </Typography>
                            )}
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                {/* User Behavior Analysis */}
                <Grid item xs={12} lg={4}>
                    <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                                <AnalyticsIcon sx={{ mr: 1 }} />
                                User Behavior Analysis
                                <Tooltip title="View behavior details (Alt+U)">
                                    <IconButton 
                                        size="small" 
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            showDetails('behavior', userBehaviorInsights);
                                        }}
                                        sx={{ ml: 1 }}
                                    >
                                        <VisibilityIcon fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                            </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {userBehaviorInsights ? (
                                <Box>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>Pattern:</strong> {userBehaviorInsights.behavior_pattern}
                                    </Typography>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>User ID:</strong> {userBehaviorInsights.user_id}
                                    </Typography>
                                    
                                    <Box sx={{ mt: 2 }}>
                                        <Typography variant="body2" gutterBottom>
                                            Anomaly Score
                                        </Typography>
                                        <LinearProgress 
                                            variant="determinate" 
                                            value={(userBehaviorInsights.anomaly_score || 0) * 100}
                                            color={(userBehaviorInsights.anomaly_score || 0) > 0.5 ? 'warning' : 'success'}
                                            sx={{ height: 8, borderRadius: 4 }}
                                        />
                                        <Typography variant="caption" color="textSecondary">
                                            {((userBehaviorInsights.anomaly_score || 0) * 100).toFixed(1)}%
                                        </Typography>
                                    </Box>

                                    {userBehaviorInsights.recommendations && (
                                        <Box sx={{ mt: 2 }}>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>AI Recommendations:</strong>
                                            </Typography>
                                            <List dense>
                                                {userBehaviorInsights.recommendations.map((rec, index) => (
                                                    <ListItem key={index} sx={{ pl: 0 }}>
                                                        <ListItemIcon>
                                                            <TrendingUpIcon fontSize="small" color="primary" />
                                                        </ListItemIcon>
                                                        <ListItemText 
                                                            primary={rec}
                                                            primaryTypographyProps={{ variant: 'body2' }}
                                                        />
                                                    </ListItem>
                                                ))}
                                            </List>
                                        </Box>
                                    )}

                                    {userBehaviorInsights.accessibility_needs && (
                                        <Box sx={{ mt: 2 }}>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Accessibility Needs:</strong>
                                            </Typography>
                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                                {userBehaviorInsights.accessibility_needs.map((need, index) => (
                                                    <Chip 
                                                        key={index}
                                                        label={need}
                                                        size="small"
                                                        color="primary"
                                                        variant="outlined"
                                                    />
                                                ))}
                                            </Box>
                                        </Box>
                                    )}
                                </Box>
                            ) : (
                                <Typography variant="body2" color="textSecondary">
                                    No user behavior analysis available
                                </Typography>
                            )}
                        </AccordionDetails>
                    </Accordion>
                </Grid>
            </Grid>

            {/* AI Capabilities Chart */}
            <Grid container spacing={3} sx={{ mt: 3 }}>
                <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            AI Capability Assessment
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Radar 
                                data={aiCapabilitiesData}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        r: {
                                            beginAtZero: true,
                                            max: 100,
                                            ticks: {
                                                stepSize: 20
                                            }
                                        }
                                    }
                                }}
                            />
                        </Box>
                    </Paper>
                </Grid>

                <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            AI System Status
                        </Typography>
                        <List>
                            <ListItem>
                                <ListItemIcon>
                                    <CheckCircleIcon color="success" />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Real-time Processing"
                                    secondary={aiStatus.real_time_processing ? 'Active' : 'Inactive'}
                                />
                            </ListItem>
                            <ListItem>
                                <ListItemIcon>
                                    <CheckCircleIcon color="success" />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Learning Enabled"
                                    secondary={aiStatus.learning_enabled ? 'Active' : 'Inactive'}
                                />
                            </ListItem>
                            <ListItem>
                                <ListItemIcon>
                                    <CheckCircleIcon color="success" />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Background Processing"
                                    secondary={aiStatus.background_processing ? 'Active' : 'Inactive'}
                                />
                            </ListItem>
                            <ListItem>
                                <ListItemIcon>
                                    <AssessmentIcon color="primary" />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Threat History"
                                    secondary={`${aiStatus.threat_history_size || 0} entries`}
                                />
                            </ListItem>
                            <ListItem>
                                <ListItemIcon>
                                    <PersonIcon color="primary" />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="User Behavior Cache"
                                    secondary={`${aiStatus.user_behavior_cache_size || 0} profiles`}
                                />
                            </ListItem>
                        </List>
                    </Paper>
                </Grid>
            </Grid>

            {/* Details Dialog */}
            <Dialog 
                open={detailsDialog.open} 
                onClose={() => setDetailsDialog({ open: false, type: null, data: null })}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>
                    {detailsDialog.type === 'threat' && 'Threat Analysis Details'}
                    {detailsDialog.type === 'performance' && 'Performance Optimization Details'}
                    {detailsDialog.type === 'behavior' && 'User Behavior Analysis Details'}
                </DialogTitle>
                <DialogContent>
                    {detailsDialog.data && (
                        <Box>
                            <pre style={{ 
                                background: theme.palette.grey[100], 
                                padding: 16, 
                                borderRadius: 4,
                                overflow: 'auto',
                                fontSize: '0.875rem',
                                fontFamily: 'monospace'
                            }}>
                                {JSON.stringify(detailsDialog.data, null, 2)}
                            </pre>
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDetailsDialog({ open: false, type: null, data: null })}>
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default AIInsights;
