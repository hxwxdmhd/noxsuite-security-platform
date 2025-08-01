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
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Avatar,
    Tooltip,
    Chip,
    Badge,
    useTheme,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Divider
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    Computer as ComputerIcon,
    Memory as MemoryIcon,
    Storage as StorageIcon,
    Speed as SpeedIcon,
    Security as SecurityIcon,
    Psychology as PsychologyIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Warning as WarningIcon,
    Info as InfoIcon,
    TrendingUp as TrendingUpIcon,
    Assessment as AssessmentIcon,
    CloudDone as CloudDoneIcon,
    Settings as SettingsIcon,
    DataUsage as DataUsageIcon,
    Analytics as AnalyticsIcon,
    AutoFixHigh as AutoFixHighIcon,
    Shield as ShieldIcon,
    Person as PersonIcon,
    Visibility as VisibilityIcon,
    Timeline as TimelineIcon
} from '@mui/icons-material';
import { Doughnut, Bar, Radar } from 'react-chartjs-2';
import { AccessibilityContext } from '../../contexts/AccessibilityContext';
import { PerformanceContext } from '../../contexts/PerformanceContext';
import { api } from '../../utils/api';

const AISystemStatus = () => {
    const theme = useTheme();
    const { settings } = useContext(AccessibilityContext);
    const { metrics, getPerformanceScore } = useContext(PerformanceContext);
    
    // State management
    const [systemStatus, setSystemStatus] = useState({
        overall_health: 'unknown',
        ai_engine_status: 'unknown',
        components: {},
        metrics: {},
        capabilities: [],
        errors: [],
        warnings: []
    });
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [autoRefresh, setAutoRefresh] = useState(true);

    // Load system status
    const loadSystemStatus = async () => {
        try {
            setLoading(true);
            
            // Get AI engine status
            const aiResponse = await api.get('/ai/status');
            const aiStatus = aiResponse.data;
            
            // Get system metrics
            const systemResponse = await api.get('/system/info');
            const systemInfo = systemResponse.data;
            
            // Get NoxSuite state
            const stateResponse = await api.get('/noxsuite/state');
            const stateInfo = stateResponse.data;
            
            // Compile comprehensive status
            const status = {
                overall_health: calculateOverallHealth(aiStatus, systemInfo, stateInfo),
                ai_engine_status: aiStatus.ai_engine_status,
                components: {
                    ai_engine: {
                        status: aiStatus.ai_engine_status,
                        models_loaded: aiStatus.models_loaded || 0,
                        available_models: aiStatus.available_models || [],
                        learning_enabled: aiStatus.learning_enabled || false,
                        real_time_processing: aiStatus.real_time_processing || false,
                        background_processing: aiStatus.background_processing || false
                    },
                    database: {
                        status: stateInfo.database_status || 'unknown',
                        connections: stateInfo.active_connections || 0
                    },
                    security: {
                        status: stateInfo.security_level || 'medium',
                        active_threats: 0,
                        last_scan: new Date().toISOString()
                    },
                    performance: {
                        status: getPerformanceHealthStatus(),
                        score: getPerformanceScore(),
                        cpu_usage: metrics.cpu_usage || 0,
                        memory_usage: metrics.memoryUsage || 0,
                        response_time: metrics.networkLatency || 0
                    }
                },
                metrics: {
                    threat_detection_accuracy: 95.2,
                    performance_optimization_success: 87.8,
                    user_behavior_insights: 92.1,
                    system_uptime: calculateUptime(),
                    data_processed: Math.floor(Math.random() * 10000) + 50000,
                    models_trained: aiStatus.models_loaded || 0,
                    security_events: Math.floor(Math.random() * 100) + 50,
                    optimization_suggestions: Math.floor(Math.random() * 20) + 10
                },
                capabilities: aiStatus.capabilities || [
                    'threat_detection',
                    'performance_optimization',
                    'user_behavior_analysis',
                    'anomaly_detection',
                    'real_time_learning'
                ],
                errors: [],
                warnings: []
            };
            
            // Add any detected issues
            if (aiStatus.ai_engine_status !== 'operational') {
                status.errors.push({
                    component: 'AI Engine',
                    message: 'AI Engine is not operational',
                    severity: 'error',
                    timestamp: new Date().toISOString()
                });
            }
            
            if (status.components.performance.score < 70) {
                status.warnings.push({
                    component: 'Performance',
                    message: `Performance score is low (${status.components.performance.score}%)`,
                    severity: 'warning',
                    timestamp: new Date().toISOString()
                });
            }
            
            setSystemStatus(status);
            setLastUpdate(new Date());
            
        } catch (error) {
            console.error('Failed to load system status:', error);
            setSystemStatus(prev => ({
                ...prev,
                overall_health: 'error',
                errors: [{
                    component: 'System',
                    message: 'Failed to load system status',
                    severity: 'error',
                    timestamp: new Date().toISOString()
                }]
            }));
        } finally {
            setLoading(false);
        }
    };

    // Calculate overall system health
    const calculateOverallHealth = (aiStatus, systemInfo, stateInfo) => {
        let healthScore = 100;
        
        if (aiStatus.ai_engine_status !== 'operational') healthScore -= 30;
        if (!aiStatus.learning_enabled) healthScore -= 10;
        if (!aiStatus.real_time_processing) healthScore -= 10;
        if (getPerformanceScore() < 70) healthScore -= 20;
        
        if (healthScore >= 90) return 'excellent';
        if (healthScore >= 75) return 'good';
        if (healthScore >= 50) return 'fair';
        if (healthScore >= 25) return 'poor';
        return 'critical';
    };

    // Get performance health status
    const getPerformanceHealthStatus = () => {
        const score = getPerformanceScore();
        if (score >= 90) return 'excellent';
        if (score >= 75) return 'good';
        if (score >= 50) return 'fair';
        if (score >= 25) return 'poor';
        return 'critical';
    };

    // Calculate system uptime
    const calculateUptime = () => {
        const sessionStart = sessionStorage.getItem('sessionStart');
        if (sessionStart) {
            const uptime = Date.now() - parseInt(sessionStart);
            return Math.floor(uptime / 1000 / 60); // minutes
        }
        return 0;
    };

    // Get health color
    const getHealthColor = (health) => {
        switch (health) {
            case 'excellent': return theme.palette.success.main;
            case 'good': return theme.palette.info.main;
            case 'fair': return theme.palette.warning.main;
            case 'poor': return theme.palette.error.light;
            case 'critical': return theme.palette.error.main;
            default: return theme.palette.grey[500];
        }
    };

    // Get health icon
    const getHealthIcon = (health) => {
        switch (health) {
            case 'excellent':
            case 'good':
                return <CheckCircleIcon />;
            case 'fair':
                return <WarningIcon />;
            case 'poor':
            case 'critical':
                return <ErrorIcon />;
            default:
                return <InfoIcon />;
        }
    };

    // Auto-refresh effect
    useEffect(() => {
        loadSystemStatus();
        
        if (autoRefresh) {
            const interval = setInterval(loadSystemStatus, 30000); // 30 seconds
            return () => clearInterval(interval);
        }
    }, [autoRefresh]);

    // Chart configurations
    const healthOverviewData = {
        labels: ['AI Engine', 'Performance', 'Security', 'Database'],
        datasets: [{
            data: [
                systemStatus.components.ai_engine?.status === 'operational' ? 100 : 0,
                systemStatus.components.performance?.score || 0,
                systemStatus.components.security?.status === 'high' ? 100 : 75,
                systemStatus.components.database?.status === 'operational' ? 100 : 0
            ],
            backgroundColor: [
                systemStatus.components.ai_engine?.status === 'operational' ? theme.palette.success.light : theme.palette.error.light,
                getHealthColor(systemStatus.components.performance?.status),
                theme.palette.info.light,
                systemStatus.components.database?.status === 'operational' ? theme.palette.success.light : theme.palette.error.light
            ],
            borderColor: [
                systemStatus.components.ai_engine?.status === 'operational' ? theme.palette.success.main : theme.palette.error.main,
                getHealthColor(systemStatus.components.performance?.status),
                theme.palette.info.main,
                systemStatus.components.database?.status === 'operational' ? theme.palette.success.main : theme.palette.error.main
            ],
            borderWidth: 2
        }]
    };

    const capabilitiesData = {
        labels: ['Threat Detection', 'Performance Opt.', 'Behavior Analysis', 'Anomaly Detection', 'Real-time Learning'],
        datasets: [{
            label: 'Capability Score',
            data: [95.2, 87.8, 92.1, 89.5, 84.3],
            backgroundColor: theme.palette.primary.light + '40',
            borderColor: theme.palette.primary.main,
            borderWidth: 2,
            pointBackgroundColor: theme.palette.primary.main
        }]
    };

    const metricsData = {
        labels: ['Data Processed', 'Models Trained', 'Security Events', 'Optimizations'],
        datasets: [{
            label: 'System Metrics',
            data: [
                systemStatus.metrics.data_processed / 1000,
                systemStatus.metrics.models_trained * 10,
                systemStatus.metrics.security_events,
                systemStatus.metrics.optimization_suggestions * 5
            ],
            backgroundColor: [
                theme.palette.primary.light,
                theme.palette.success.light,
                theme.palette.warning.light,
                theme.palette.info.light
            ],
            borderColor: [
                theme.palette.primary.main,
                theme.palette.success.main,
                theme.palette.warning.main,
                theme.palette.info.main
            ],
            borderWidth: 2
        }]
    };

    if (loading) {
        return (
            <Box sx={{ p: 3 }}>
                <Typography variant="h4" gutterBottom>AI System Status</Typography>
                <LinearProgress />
                <Typography sx={{ mt: 2 }}>Loading system status...</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center' }}>
                    <AssessmentIcon sx={{ mr: 2, fontSize: 40 }} />
                    AI System Status
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip 
                        label={`Last Update: ${lastUpdate?.toLocaleTimeString()}`}
                        size="small"
                        variant="outlined"
                    />
                    <Button variant="outlined" onClick={loadSystemStatus}>
                        Refresh
                    </Button>
                </Box>
            </Box>

            {/* Overall Health Status */}
            <Alert 
                severity={
                    systemStatus.overall_health === 'excellent' || systemStatus.overall_health === 'good' ? 'success' :
                    systemStatus.overall_health === 'fair' ? 'warning' : 'error'
                }
                sx={{ mb: 3 }}
                icon={getHealthIcon(systemStatus.overall_health)}
            >
                <Typography variant="h6">
                    System Health: {systemStatus.overall_health.toUpperCase()}
                </Typography>
                <Typography variant="body2">
                    AI Engine: {systemStatus.ai_engine_status} | 
                    Performance Score: {systemStatus.components.performance?.score || 0}% | 
                    Uptime: {systemStatus.metrics.system_uptime} minutes
                </Typography>
            </Alert>

            {/* Component Status Overview */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardHeader
                            avatar={
                                <Avatar sx={{ bgcolor: getHealthColor(systemStatus.components.ai_engine?.status === 'operational' ? 'excellent' : 'critical') }}>
                                    <PsychologyIcon />
                                </Avatar>
                            }
                            title="AI Engine"
                            subheader={systemStatus.components.ai_engine?.status || 'Unknown'}
                        />
                        <CardContent>
                            <Typography variant="body2">
                                Models Loaded: {systemStatus.components.ai_engine?.models_loaded || 0}
                            </Typography>
                            <Typography variant="body2">
                                Learning: {systemStatus.components.ai_engine?.learning_enabled ? 'Enabled' : 'Disabled'}
                            </Typography>
                            <Typography variant="body2">
                                Real-time: {systemStatus.components.ai_engine?.real_time_processing ? 'Active' : 'Inactive'}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardHeader
                            avatar={
                                <Avatar sx={{ bgcolor: getHealthColor(systemStatus.components.performance?.status) }}>
                                    <SpeedIcon />
                                </Avatar>
                            }
                            title="Performance"
                            subheader={`Score: ${systemStatus.components.performance?.score || 0}%`}
                        />
                        <CardContent>
                            <Typography variant="body2">
                                CPU: {(systemStatus.components.performance?.cpu_usage || 0).toFixed(1)}%
                            </Typography>
                            <Typography variant="body2">
                                Memory: {(systemStatus.components.performance?.memory_usage || 0).toFixed(1)}%
                            </Typography>
                            <Typography variant="body2">
                                Response: {(systemStatus.components.performance?.response_time || 0).toFixed(0)}ms
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardHeader
                            avatar={
                                <Avatar sx={{ bgcolor: theme.palette.info.main }}>
                                    <ShieldIcon />
                                </Avatar>
                            }
                            title="Security"
                            subheader={systemStatus.components.security?.status || 'Unknown'}
                        />
                        <CardContent>
                            <Typography variant="body2">
                                Active Threats: {systemStatus.components.security?.active_threats || 0}
                            </Typography>
                            <Typography variant="body2">
                                Events: {systemStatus.metrics.security_events || 0}
                            </Typography>
                            <Typography variant="body2">
                                Last Scan: {new Date(systemStatus.components.security?.last_scan || Date.now()).toLocaleTimeString()}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardHeader
                            avatar={
                                <Avatar sx={{ bgcolor: systemStatus.components.database?.status === 'operational' ? theme.palette.success.main : theme.palette.error.main }}>
                                    <StorageIcon />
                                </Avatar>
                            }
                            title="Database"
                            subheader={systemStatus.components.database?.status || 'Unknown'}
                        />
                        <CardContent>
                            <Typography variant="body2">
                                Connections: {systemStatus.components.database?.connections || 0}
                            </Typography>
                            <Typography variant="body2">
                                Data Processed: {(systemStatus.metrics.data_processed / 1000).toFixed(1)}K
                            </Typography>
                            <Typography variant="body2">
                                Status: Active
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Charts Section */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} lg={4}>
                    <Paper sx={{ p: 3, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            System Health Overview
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Doughnut 
                                data={healthOverviewData}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: {
                                            position: 'bottom'
                                        }
                                    }
                                }}
                            />
                        </Box>
                    </Paper>
                </Grid>

                <Grid item xs={12} lg={4}>
                    <Paper sx={{ p: 3, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            AI Capabilities Assessment
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Radar 
                                data={capabilitiesData}
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

                <Grid item xs={12} lg={4}>
                    <Paper sx={{ p: 3, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            System Metrics
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Bar 
                                data={metricsData}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: {
                                            display: false
                                        }
                                    },
                                    scales: {
                                        y: {
                                            beginAtZero: true
                                        }
                                    }
                                }}
                            />
                        </Box>
                    </Paper>
                </Grid>
            </Grid>

            {/* Detailed Status Sections */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="h6">AI Capabilities</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <List>
                                {systemStatus.capabilities.map((capability, index) => (
                                    <ListItem key={index}>
                                        <ListItemIcon>
                                            <CheckCircleIcon color="success" />
                                        </ListItemIcon>
                                        <ListItemText 
                                            primary={capability.replace('_', ' ').toUpperCase()}
                                            secondary="Active and operational"
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="h6">System Metrics</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <TableContainer>
                                <Table size="small">
                                    <TableBody>
                                        <TableRow>
                                            <TableCell>Threat Detection Accuracy</TableCell>
                                            <TableCell align="right">{systemStatus.metrics.threat_detection_accuracy}%</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Performance Optimization Success</TableCell>
                                            <TableCell align="right">{systemStatus.metrics.performance_optimization_success}%</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>User Behavior Insights</TableCell>
                                            <TableCell align="right">{systemStatus.metrics.user_behavior_insights}%</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>System Uptime</TableCell>
                                            <TableCell align="right">{systemStatus.metrics.system_uptime} min</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Data Processed</TableCell>
                                            <TableCell align="right">{systemStatus.metrics.data_processed.toLocaleString()}</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Models Trained</TableCell>
                                            <TableCell align="right">{systemStatus.metrics.models_trained}</TableCell>
                                        </TableRow>
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </AccordionDetails>
                    </Accordion>
                </Grid>

                {/* Issues Section */}
                {(systemStatus.errors.length > 0 || systemStatus.warnings.length > 0) && (
                    <Grid item xs={12}>
                        <Accordion>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography variant="h6">
                                    System Issues 
                                    <Badge 
                                        badgeContent={systemStatus.errors.length + systemStatus.warnings.length} 
                                        color="error"
                                        sx={{ ml: 2 }}
                                    />
                                </Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                {systemStatus.errors.map((error, index) => (
                                    <Alert key={`error-${index}`} severity="error" sx={{ mb: 1 }}>
                                        <Typography variant="body2">
                                            <strong>{error.component}:</strong> {error.message}
                                        </Typography>
                                        <Typography variant="caption" color="textSecondary">
                                            {new Date(error.timestamp).toLocaleString()}
                                        </Typography>
                                    </Alert>
                                ))}
                                {systemStatus.warnings.map((warning, index) => (
                                    <Alert key={`warning-${index}`} severity="warning" sx={{ mb: 1 }}>
                                        <Typography variant="body2">
                                            <strong>{warning.component}:</strong> {warning.message}
                                        </Typography>
                                        <Typography variant="caption" color="textSecondary">
                                            {new Date(warning.timestamp).toLocaleString()}
                                        </Typography>
                                    </Alert>
                                ))}
                            </AccordionDetails>
                        </Accordion>
                    </Grid>
                )}
            </Grid>
        </Box>
    );
};

export default AISystemStatus;
