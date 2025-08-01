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
    Avatar,
    Tooltip,
    IconButton,
    Switch,
    FormControlLabel,
    Slider,
    useTheme,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Accordion,
    AccordionSummary,
    AccordionDetails
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    PlayArrow as PlayArrowIcon,
    Pause as PauseIcon,
    Security as SecurityIcon,
    Speed as SpeedIcon,
    Person as PersonIcon,
    Timeline as TimelineIcon,
    Assessment as AssessmentIcon,
    Settings as SettingsIcon,
    Visibility as VisibilityIcon,
    VisibilityOff as VisibilityOffIcon,
    AutoFixHigh as AutoFixHighIcon,
    Psychology as PsychologyIcon,
    Shield as ShieldIcon,
    TrendingUp as TrendingUpIcon,
    Warning as WarningIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Refresh as RefreshIcon
} from '@mui/icons-material';
import { Line, Doughnut, Radar, Scatter } from 'react-chartjs-2';
import { AccessibilityContext } from '../../contexts/AccessibilityContext';
import { PerformanceContext } from '../../contexts/PerformanceContext';
import { api } from '../../utils/api';

const RealTimeAIMonitor = () => {
    const theme = useTheme();
    const { settings } = useContext(AccessibilityContext);
    const { metrics } = useContext(PerformanceContext);
    
    // State management
    const [isMonitoring, setIsMonitoring] = useState(false);
    const [realTimeData, setRealTimeData] = useState({
        threats: [],
        performance: [],
        behavior: [],
        anomalies: []
    });
    const [currentAnalysis, setCurrentAnalysis] = useState({
        threat: null,
        performance: null,
        behavior: null
    });
    const [settings_local, setSettingsLocal] = useState({
        updateInterval: 5000, // 5 seconds
        maxDataPoints: 50,
        enableThreatMonitoring: true,
        enablePerformanceMonitoring: true,
        enableBehaviorMonitoring: true,
        alertThreshold: 0.7
    });
    const [alerts, setAlerts] = useState([]);
    const [settingsDialog, setSettingsDialog] = useState(false);
    const [detailsDialog, setDetailsDialog] = useState({ open: false, type: null, data: null });

    // Real-time monitoring effect
    useEffect(() => {
        let interval;
        
        if (isMonitoring) {
            interval = setInterval(async () => {
                await performRealTimeAnalysis();
            }, settings_local.updateInterval);
        }
        
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [isMonitoring, settings_local.updateInterval]);

    // Perform real-time AI analysis
    const performRealTimeAnalysis = async () => {
        try {
            const timestamp = new Date().toISOString();
            
            // Threat Analysis
            if (settings_local.enableThreatMonitoring) {
                const threatData = {
                    source_ip: window.location.hostname,
                    user_agent: navigator.userAgent,
                    request_frequency: Math.random() * 10,
                    payload_size: Math.random() * 2048,
                    response_time: performance.now(),
                    error_count: Math.floor(Math.random() * 3),
                    unique_endpoints: Math.floor(Math.random() * 10) + 1,
                    geographic_distance: Math.random() * 1000,
                    session_duration: Date.now() - (sessionStorage.getItem('sessionStart') || Date.now())
                };

                const threatResponse = await api.post('/ai/analyze_threat', threatData);
                const threatResult = { ...threatResponse.data, timestamp };
                
                setCurrentAnalysis(prev => ({ ...prev, threat: threatResult }));
                setRealTimeData(prev => ({
                    ...prev,
                    threats: [threatResult, ...prev.threats.slice(0, settings_local.maxDataPoints - 1)]
                }));

                // Check for high-risk threats
                if (threatResult.confidence > settings_local.alertThreshold) {
                    addAlert({
                        type: 'threat',
                        severity: threatResult.severity,
                        message: `High-risk ${threatResult.threat_type} detected`,
                        timestamp
                    });
                }
            }

            // Performance Analysis
            if (settings_local.enablePerformanceMonitoring) {
                const performanceData = {
                    metrics: {
                        cpu_usage: Math.random() * 100,
                        memory_usage: Math.random() * 100,
                        response_time: Math.random() * 1000,
                        error_rate: Math.random() * 5
                    }
                };

                const perfResponse = await api.post('/ai/optimize_performance', performanceData);
                const perfResult = { ...perfResponse.data, timestamp };
                
                setCurrentAnalysis(prev => ({ ...prev, performance: perfResult }));
                setRealTimeData(prev => ({
                    ...prev,
                    performance: [perfResult, ...prev.performance.slice(0, settings_local.maxDataPoints - 1)]
                }));
            }

            // User Behavior Analysis
            if (settings_local.enableBehaviorMonitoring) {
                const behaviorData = {
                    user_id: 'monitoring_user',
                    behavior_data: {
                        session_duration: Date.now() - (sessionStorage.getItem('sessionStart') || Date.now()),
                        click_frequency: Math.random() * 5,
                        page_views: parseInt(sessionStorage.getItem('pageViews') || '1'),
                        features_used: ['monitor', 'ai', 'dashboard'],
                        error_encounters: Math.floor(Math.random() * 3),
                        help_requests: Math.floor(Math.random() * 2),
                        accessibility_features_used: Object.values(settings).filter(Boolean).length,
                        response_time_variance: Math.random() * 200,
                        zoom_level: 100,
                        mouse_usage: 50 + Math.random() * 50
                    }
                };

                const behaviorResponse = await api.post('/ai/analyze_user_behavior', behaviorData);
                const behaviorResult = { ...behaviorResponse.data, timestamp };
                
                setCurrentAnalysis(prev => ({ ...prev, behavior: behaviorResult }));
                setRealTimeData(prev => ({
                    ...prev,
                    behavior: [behaviorResult, ...prev.behavior.slice(0, settings_local.maxDataPoints - 1)]
                }));

                // Check for behavioral anomalies
                if (behaviorResult.anomaly_score > settings_local.alertThreshold) {
                    addAlert({
                        type: 'behavior',
                        severity: 'medium',
                        message: `Unusual behavior pattern detected: ${behaviorResult.behavior_pattern}`,
                        timestamp
                    });
                }
            }

        } catch (error) {
            console.error('Real-time analysis error:', error);
            addAlert({
                type: 'system',
                severity: 'high',
                message: 'Real-time monitoring error',
                timestamp: new Date().toISOString()
            });
        }
    };

    // Add alert
    const addAlert = (alert) => {
        const newAlert = { id: Date.now(), ...alert };
        setAlerts(prev => [newAlert, ...prev.slice(0, 99)]); // Keep last 100 alerts
    };

    // Clear alerts
    const clearAlerts = () => {
        setAlerts([]);
    };

    // Toggle monitoring
    const toggleMonitoring = () => {
        setIsMonitoring(!isMonitoring);
        if (!isMonitoring) {
            // Start monitoring immediately
            performRealTimeAnalysis();
        }
    };

    // Get alert severity color
    const getAlertSeverityColor = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical': return theme.palette.error.main;
            case 'high': return theme.palette.warning.main;
            case 'medium': return theme.palette.info.main;
            case 'low': return theme.palette.success.main;
            default: return theme.palette.grey[500];
        }
    };

    // Chart configurations
    const threatTrendData = {
        labels: realTimeData.threats.slice().reverse().map((_, index) => `T-${index * (settings_local.updateInterval / 1000)}s`),
        datasets: [{
            label: 'Threat Confidence',
            data: realTimeData.threats.slice().reverse().map(t => (t.confidence || 0) * 100),
            borderColor: theme.palette.error.main,
            backgroundColor: theme.palette.error.light + '20',
            fill: true,
            tension: 0.4
        }]
    };

    const performanceTrendData = {
        labels: realTimeData.performance.slice().reverse().map((_, index) => `T-${index * (settings_local.updateInterval / 1000)}s`),
        datasets: [{
            label: 'Performance Score',
            data: realTimeData.performance.slice().reverse().map(p => p.improvement_percentage || 0),
            borderColor: theme.palette.success.main,
            backgroundColor: theme.palette.success.light + '20',
            fill: true,
            tension: 0.4
        }]
    };

    const behaviorAnomalyData = {
        labels: realTimeData.behavior.slice().reverse().map((_, index) => `T-${index * (settings_local.updateInterval / 1000)}s`),
        datasets: [{
            label: 'Anomaly Score',
            data: realTimeData.behavior.slice().reverse().map(b => (b.anomaly_score || 0) * 100),
            borderColor: theme.palette.warning.main,
            backgroundColor: theme.palette.warning.light + '20',
            fill: true,
            tension: 0.4
        }]
    };

    const aiActivityData = {
        labels: ['Threat Detection', 'Performance Optimization', 'Behavior Analysis', 'Real-time Processing'],
        datasets: [{
            data: [
                realTimeData.threats.length,
                realTimeData.performance.length,
                realTimeData.behavior.length,
                isMonitoring ? 100 : 0
            ],
            backgroundColor: [
                theme.palette.error.light,
                theme.palette.success.light,
                theme.palette.info.light,
                theme.palette.primary.light
            ],
            borderColor: [
                theme.palette.error.main,
                theme.palette.success.main,
                theme.palette.info.main,
                theme.palette.primary.main
            ],
            borderWidth: 2
        }]
    };

    return (
        <Box sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center' }}>
                    <TimelineIcon sx={{ mr: 2, fontSize: 40 }} />
                    Real-Time AI Monitor
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={isMonitoring}
                                onChange={toggleMonitoring}
                                color="primary"
                            />
                        }
                        label={isMonitoring ? 'Monitoring Active' : 'Monitoring Inactive'}
                    />
                    
                    <Tooltip title="Monitor Settings">
                        <IconButton onClick={() => setSettingsDialog(true)} color="primary">
                            <SettingsIcon />
                        </IconButton>
                    </Tooltip>
                    
                    <Tooltip title="Manual Refresh">
                        <IconButton onClick={performRealTimeAnalysis} color="primary">
                            <RefreshIcon />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Box>

            {/* Monitoring Status */}
            <Alert 
                severity={isMonitoring ? 'success' : 'warning'} 
                sx={{ mb: 3 }}
                action={
                    <Button color="inherit" onClick={toggleMonitoring}>
                        {isMonitoring ? <PauseIcon /> : <PlayArrowIcon />}
                        {isMonitoring ? 'Stop' : 'Start'}
                    </Button>
                }
            >
                Real-time AI monitoring is {isMonitoring ? 'active' : 'inactive'}. 
                {isMonitoring && ` Update interval: ${settings_local.updateInterval / 1000}s`}
            </Alert>

            {/* Current Analysis Overview */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardHeader
                            avatar={
                                <Avatar sx={{ bgcolor: getAlertSeverityColor(currentAnalysis.threat?.severity) }}>
                                    <SecurityIcon />
                                </Avatar>
                            }
                            title="Current Threat Status"
                            action={
                                <IconButton onClick={() => setDetailsDialog({ open: true, type: 'threat', data: currentAnalysis.threat })}>
                                    <VisibilityIcon />
                                </IconButton>
                            }
                        />
                        <CardContent>
                            {currentAnalysis.threat ? (
                                <>
                                    <Typography variant="h6" color={getAlertSeverityColor(currentAnalysis.threat.severity)}>
                                        {currentAnalysis.threat.threat_type}
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary" gutterBottom>
                                        Confidence: {((currentAnalysis.threat.confidence || 0) * 100).toFixed(1)}%
                                    </Typography>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={(currentAnalysis.threat.confidence || 0) * 100}
                                        sx={{ mt: 1, height: 8, borderRadius: 4 }}
                                        color={currentAnalysis.threat.confidence > 0.5 ? 'error' : 'success'}
                                    />
                                </>
                            ) : (
                                <Typography variant="body2" color="textSecondary">
                                    No threat analysis available
                                </Typography>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardHeader
                            avatar={
                                <Avatar sx={{ bgcolor: theme.palette.success.main }}>
                                    <AutoFixHighIcon />
                                </Avatar>
                            }
                            title="Performance Status"
                            action={
                                <IconButton onClick={() => setDetailsDialog({ open: true, type: 'performance', data: currentAnalysis.performance })}>
                                    <VisibilityIcon />
                                </IconButton>
                            }
                        />
                        <CardContent>
                            {currentAnalysis.performance ? (
                                <>
                                    <Typography variant="h6" color="success.main">
                                        {currentAnalysis.performance.component}
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary" gutterBottom>
                                        Improvement: +{(currentAnalysis.performance.improvement_percentage || 0).toFixed(1)}%
                                    </Typography>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={Math.min(currentAnalysis.performance.improvement_percentage || 0, 100)}
                                        color="success"
                                        sx={{ mt: 1, height: 8, borderRadius: 4 }}
                                    />
                                </>
                            ) : (
                                <Typography variant="body2" color="textSecondary">
                                    No performance analysis available
                                </Typography>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardHeader
                            avatar={
                                <Avatar sx={{ bgcolor: theme.palette.info.main }}>
                                    <PersonIcon />
                                </Avatar>
                            }
                            title="Behavior Status"
                            action={
                                <IconButton onClick={() => setDetailsDialog({ open: true, type: 'behavior', data: currentAnalysis.behavior })}>
                                    <VisibilityIcon />
                                </IconButton>
                            }
                        />
                        <CardContent>
                            {currentAnalysis.behavior ? (
                                <>
                                    <Typography variant="h6" color="info.main">
                                        {currentAnalysis.behavior.behavior_pattern}
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary" gutterBottom>
                                        Anomaly: {((currentAnalysis.behavior.anomaly_score || 0) * 100).toFixed(1)}%
                                    </Typography>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={(currentAnalysis.behavior.anomaly_score || 0) * 100}
                                        color={(currentAnalysis.behavior.anomaly_score || 0) > 0.5 ? 'warning' : 'success'}
                                        sx={{ mt: 1, height: 8, borderRadius: 4 }}
                                    />
                                </>
                            ) : (
                                <Typography variant="body2" color="textSecondary">
                                    No behavior analysis available
                                </Typography>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Real-time Charts */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 3, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            Threat Detection Timeline
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Line 
                                data={threatTrendData}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            max: 100,
                                            title: {
                                                display: true,
                                                text: 'Confidence %'
                                            }
                                        },
                                        x: {
                                            title: {
                                                display: true,
                                                text: 'Time'
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: true
                                        }
                                    }
                                }}
                            />
                        </Box>
                    </Paper>
                </Grid>

                <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 3, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            Performance Optimization Timeline
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Line 
                                data={performanceTrendData}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            title: {
                                                display: true,
                                                text: 'Improvement %'
                                            }
                                        },
                                        x: {
                                            title: {
                                                display: true,
                                                text: 'Time'
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: true
                                        }
                                    }
                                }}
                            />
                        </Box>
                    </Paper>
                </Grid>

                <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 3, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            Behavior Anomaly Timeline
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Line 
                                data={behaviorAnomalyData}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            max: 100,
                                            title: {
                                                display: true,
                                                text: 'Anomaly Score %'
                                            }
                                        },
                                        x: {
                                            title: {
                                                display: true,
                                                text: 'Time'
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: true
                                        }
                                    }
                                }}
                            />
                        </Box>
                    </Paper>
                </Grid>

                <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 3, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            AI Activity Overview
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Doughnut 
                                data={aiActivityData}
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
            </Grid>

            {/* Alerts Section */}
            <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                        Real-time Alerts ({alerts.length})
                    </Typography>
                    <Button onClick={clearAlerts} disabled={alerts.length === 0}>
                        Clear All
                    </Button>
                </Box>
                
                {alerts.length > 0 ? (
                    <TableContainer sx={{ maxHeight: 300 }}>
                        <Table size="small" stickyHeader>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Type</TableCell>
                                    <TableCell>Severity</TableCell>
                                    <TableCell>Message</TableCell>
                                    <TableCell>Time</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {alerts.slice(0, 20).map((alert) => (
                                    <TableRow key={alert.id}>
                                        <TableCell>
                                            <Chip 
                                                label={alert.type} 
                                                size="small" 
                                                variant="outlined"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={alert.severity}
                                                size="small"
                                                sx={{ 
                                                    bgcolor: getAlertSeverityColor(alert.severity) + '20',
                                                    color: getAlertSeverityColor(alert.severity)
                                                }}
                                            />
                                        </TableCell>
                                        <TableCell>{alert.message}</TableCell>
                                        <TableCell>
                                            {new Date(alert.timestamp).toLocaleTimeString()}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                ) : (
                    <Typography variant="body2" color="textSecondary">
                        No alerts to display
                    </Typography>
                )}
            </Paper>

            {/* Settings Dialog */}
            <Dialog open={settingsDialog} onClose={() => setSettingsDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Monitor Settings</DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2 }}>
                        <Typography gutterBottom>Update Interval (seconds)</Typography>
                        <Slider
                            value={settings_local.updateInterval / 1000}
                            onChange={(e, value) => setSettingsLocal(prev => ({ ...prev, updateInterval: value * 1000 }))}
                            min={1}
                            max={60}
                            step={1}
                            marks
                            valueLabelDisplay="auto"
                            sx={{ mb: 3 }}
                        />
                        
                        <Typography gutterBottom>Max Data Points</Typography>
                        <Slider
                            value={settings_local.maxDataPoints}
                            onChange={(e, value) => setSettingsLocal(prev => ({ ...prev, maxDataPoints: value }))}
                            min={10}
                            max={100}
                            step={5}
                            marks
                            valueLabelDisplay="auto"
                            sx={{ mb: 3 }}
                        />
                        
                        <Typography gutterBottom>Alert Threshold</Typography>
                        <Slider
                            value={settings_local.alertThreshold}
                            onChange={(e, value) => setSettingsLocal(prev => ({ ...prev, alertThreshold: value }))}
                            min={0.1}
                            max={1.0}
                            step={0.1}
                            marks
                            valueLabelDisplay="auto"
                            sx={{ mb: 3 }}
                        />
                        
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={settings_local.enableThreatMonitoring}
                                    onChange={(e) => setSettingsLocal(prev => ({ ...prev, enableThreatMonitoring: e.target.checked }))}
                                />
                            }
                            label="Enable Threat Monitoring"
                            sx={{ display: 'block', mb: 1 }}
                        />
                        
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={settings_local.enablePerformanceMonitoring}
                                    onChange={(e) => setSettingsLocal(prev => ({ ...prev, enablePerformanceMonitoring: e.target.checked }))}
                                />
                            }
                            label="Enable Performance Monitoring"
                            sx={{ display: 'block', mb: 1 }}
                        />
                        
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={settings_local.enableBehaviorMonitoring}
                                    onChange={(e) => setSettingsLocal(prev => ({ ...prev, enableBehaviorMonitoring: e.target.checked }))}
                                />
                            }
                            label="Enable Behavior Monitoring"
                            sx={{ display: 'block' }}
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setSettingsDialog(false)}>Close</Button>
                </DialogActions>
            </Dialog>

            {/* Details Dialog */}
            <Dialog 
                open={detailsDialog.open} 
                onClose={() => setDetailsDialog({ open: false, type: null, data: null })}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>
                    {detailsDialog.type === 'threat' && 'Threat Analysis Details'}
                    {detailsDialog.type === 'performance' && 'Performance Analysis Details'}
                    {detailsDialog.type === 'behavior' && 'Behavior Analysis Details'}
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

export default RealTimeAIMonitor;
