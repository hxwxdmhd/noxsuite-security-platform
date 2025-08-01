import React, { createContext, useContext, useState, useEffect } from 'react';

const PerformanceContext = createContext();

export const usePerformance = () => {
    const context = useContext(PerformanceContext);
    if (!context) {
        throw new Error('usePerformance must be used within a PerformanceProvider');
    }
    return context;
};

export const PerformanceProvider = ({ children }) => {
    // Performance metrics state
    const [metrics, setMetrics] = useState({
        loadTime: 0,
        renderTime: 0,
        networkLatency: 0,
        memoryUsage: 0,
        errorRate: 0,
        throughput: 0
    });

    // Performance optimizations state
    const [optimizations, setOptimizations] = useState([]);
    
    // Performance history
    const [history, setHistory] = useState([]);
    
    // Real-time performance monitoring
    const [monitoring, setMonitoring] = useState(true);
    
    // Performance thresholds
    const [thresholds, setThresholds] = useState({
        loadTime: 3000, // 3 seconds
        renderTime: 100, // 100ms
        networkLatency: 500, // 500ms
        memoryUsage: 80, // 80%
        errorRate: 5 // 5%
    });

    // Measure page load time
    const measureLoadTime = () => {
        if (performance && performance.timing) {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            setMetrics(prev => ({ ...prev, loadTime }));
            return loadTime;
        }
        return 0;
    };

    // Measure render time
    const measureRenderTime = (startTime) => {
        const renderTime = performance.now() - startTime;
        setMetrics(prev => ({ ...prev, renderTime }));
        return renderTime;
    };

    // Measure network latency
    const measureNetworkLatency = async (url = '/api/status') => {
        try {
            const start = performance.now();
            await fetch(url);
            const latency = performance.now() - start;
            setMetrics(prev => ({ ...prev, networkLatency: latency }));
            return latency;
        } catch (error) {
            console.error('Network latency measurement failed:', error);
            return 0;
        }
    };

    // Estimate memory usage
    const measureMemoryUsage = () => {
        if (performance && performance.memory) {
            const usage = (performance.memory.usedJSHeapSize / performance.memory.totalJSHeapSize) * 100;
            setMetrics(prev => ({ ...prev, memoryUsage: usage }));
            return usage;
        }
        return 0;
    };

    // Track error rate
    const trackError = () => {
        setMetrics(prev => ({ 
            ...prev, 
            errorRate: prev.errorRate + 1 
        }));
    };

    // Calculate throughput (operations per second)
    const updateThroughput = (operations, timeWindow = 1000) => {
        const throughput = operations / (timeWindow / 1000);
        setMetrics(prev => ({ ...prev, throughput }));
        return throughput;
    };

    // Add performance optimization
    const addOptimization = (optimization) => {
        const newOptimization = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            ...optimization
        };
        setOptimizations(prev => [newOptimization, ...prev.slice(0, 9)]); // Keep last 10
        return newOptimization;
    };

    // Get performance insights
    const getPerformanceInsights = () => {
        const insights = [];
        
        if (metrics.loadTime > thresholds.loadTime) {
            insights.push({
                type: 'warning',
                category: 'load_time',
                message: `Page load time (${(metrics.loadTime / 1000).toFixed(2)}s) exceeds threshold`,
                recommendation: 'Consider lazy loading components and optimizing bundle size'
            });
        }
        
        if (metrics.renderTime > thresholds.renderTime) {
            insights.push({
                type: 'warning',
                category: 'render_time',
                message: `Render time (${metrics.renderTime.toFixed(2)}ms) exceeds threshold`,
                recommendation: 'Use React.memo and useMemo for expensive operations'
            });
        }
        
        if (metrics.networkLatency > thresholds.networkLatency) {
            insights.push({
                type: 'warning',
                category: 'network',
                message: `Network latency (${metrics.networkLatency.toFixed(2)}ms) is high`,
                recommendation: 'Implement request caching and optimize API endpoints'
            });
        }
        
        if (metrics.memoryUsage > thresholds.memoryUsage) {
            insights.push({
                type: 'error',
                category: 'memory',
                message: `Memory usage (${metrics.memoryUsage.toFixed(1)}%) is critical`,
                recommendation: 'Check for memory leaks and cleanup event listeners'
            });
        }
        
        if (metrics.errorRate > thresholds.errorRate) {
            insights.push({
                type: 'error',
                category: 'errors',
                message: `Error rate (${metrics.errorRate}) is above threshold`,
                recommendation: 'Review error logs and implement better error handling'
            });
        }
        
        return insights;
    };

    // Performance monitoring effect
    useEffect(() => {
        if (!monitoring) return;

        // Measure initial load time
        measureLoadTime();

        // Set up periodic monitoring
        const interval = setInterval(() => {
            measureMemoryUsage();
            measureNetworkLatency();
            
            // Add to history
            const currentMetrics = {
                ...metrics,
                timestamp: new Date().toISOString()
            };
            
            setHistory(prev => [currentMetrics, ...prev.slice(0, 99)]); // Keep last 100
        }, 10000); // Every 10 seconds

        // Performance observer for navigation timing
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach((entry) => {
                        if (entry.entryType === 'navigation') {
                            setMetrics(prev => ({
                                ...prev,
                                loadTime: entry.loadEventEnd - entry.fetchStart,
                                renderTime: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart
                            }));
                        }
                    });
                });
                
                observer.observe({ entryTypes: ['navigation'] });
                
                return () => {
                    observer.disconnect();
                    clearInterval(interval);
                };
            } catch (error) {
                console.warn('PerformanceObserver not fully supported:', error);
                return () => clearInterval(interval);
            }
        }

        return () => clearInterval(interval);
    }, [monitoring, metrics]);

    // Error tracking effect
    useEffect(() => {
        const handleError = (event) => {
            trackError();
            console.error('Performance Context - Error tracked:', event.error);
        };

        const handleUnhandledRejection = (event) => {
            trackError();
            console.error('Performance Context - Promise rejection tracked:', event.reason);
        };

        window.addEventListener('error', handleError);
        window.addEventListener('unhandledrejection', handleUnhandledRejection);

        return () => {
            window.removeEventListener('error', handleError);
            window.removeEventListener('unhandledrejection', handleUnhandledRejection);
        };
    }, []);

    // Performance context value
    const value = {
        // State
        metrics,
        optimizations,
        history,
        monitoring,
        thresholds,
        
        // Actions
        setMetrics,
        setOptimizations,
        setMonitoring,
        setThresholds,
        measureLoadTime,
        measureRenderTime,
        measureNetworkLatency,
        measureMemoryUsage,
        trackError,
        updateThroughput,
        addOptimization,
        getPerformanceInsights,
        
        // Utility methods
        clearHistory: () => setHistory([]),
        resetMetrics: () => setMetrics({
            loadTime: 0,
            renderTime: 0,
            networkLatency: 0,
            memoryUsage: 0,
            errorRate: 0,
            throughput: 0
        }),
        
        // Performance scoring
        getPerformanceScore: () => {
            let score = 100;
            
            if (metrics.loadTime > thresholds.loadTime) score -= 20;
            if (metrics.renderTime > thresholds.renderTime) score -= 15;
            if (metrics.networkLatency > thresholds.networkLatency) score -= 15;
            if (metrics.memoryUsage > thresholds.memoryUsage) score -= 30;
            if (metrics.errorRate > thresholds.errorRate) score -= 20;
            
            return Math.max(0, score);
        }
    };

    return (
        <PerformanceContext.Provider value={value}>
            {children}
        </PerformanceContext.Provider>
    );
};

export { PerformanceContext };
