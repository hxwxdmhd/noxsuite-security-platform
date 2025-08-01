/**
 * Web Vitals Reporting for NoxSuite Frontend
 * Optimized for ADHD-friendly performance monitoring
 * @author @hxwxdmhd
 * @version 11.0.0
 */

const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      // Core Web Vitals - Critical for ADHD user experience
      
      // Cumulative Layout Shift - Visual stability (critical for ADHD focus)
      getCLS((metric) => {
        onPerfEntry({
          ...metric,
          adhdImpact: metric.value > 0.1 ? 'high' : metric.value > 0.05 ? 'medium' : 'low',
          adhdNote: metric.value > 0.1 
            ? 'High layout shift can be very disorienting for ADHD users'
            : 'Layout stability is good for maintaining focus'
        });
      });
      
      // First Input Delay - Responsiveness (affects ADHD immediate feedback needs)
      getFID((metric) => {
        onPerfEntry({
          ...metric,
          adhdImpact: metric.value > 100 ? 'high' : metric.value > 50 ? 'medium' : 'low',
          adhdNote: metric.value > 100
            ? 'Slow response to clicks can frustrate ADHD users'
            : 'Good responsiveness supports ADHD interaction patterns'
        });
      });
      
      // First Contentful Paint - Visual feedback (critical for ADHD attention)
      getFCP((metric) => {
        onPerfEntry({
          ...metric,
          adhdImpact: metric.value > 2000 ? 'high' : metric.value > 1000 ? 'medium' : 'low',
          adhdNote: metric.value > 2000
            ? 'Slow initial loading can cause ADHD users to lose focus'
            : 'Fast initial loading helps maintain ADHD attention'
        });
      });
      
      // Largest Contentful Paint - Perceived loading (affects ADHD waiting tolerance)
      getLCP((metric) => {
        onPerfEntry({
          ...metric,
          adhdImpact: metric.value > 3000 ? 'high' : metric.value > 2000 ? 'medium' : 'low',
          adhdNote: metric.value > 3000
            ? 'Long loading times can overwhelm ADHD users'
            : 'Good loading speed supports sustained ADHD attention'
        });
      });
      
      // Time to First Byte - Server responsiveness
      getTTFB((metric) => {
        onPerfEntry({
          ...metric,
          adhdImpact: metric.value > 800 ? 'high' : metric.value > 400 ? 'medium' : 'low',
          adhdNote: metric.value > 800
            ? 'Slow server response affects overall ADHD user experience'
            : 'Fast server response supports quick ADHD task switching'
        });
      });
      
    }).catch((error) => {
      console.warn('📊 Web Vitals could not be loaded:', error);
    });
  }
};

export { reportWebVitals };
