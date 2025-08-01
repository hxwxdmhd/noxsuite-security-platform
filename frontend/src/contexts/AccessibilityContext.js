/**
 * Accessibility Context for ADHD-Friendly Features
 * Provides comprehensive accessibility state management and WCAG 2.1 AA compliance
 * @author @hxwxdmhd
 * @version 1.0.0
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react';

// ADHD-friendly accessibility state
const initialState = {
  // Visual accessibility
  highContrast: false,
  reducedMotion: false,
  fontSize: 'medium', // small, medium, large, extra-large
  lineHeight: 1.5,
  letterSpacing: 0,
  
  // Focus management
  enhancedFocus: true,
  focusRingWidth: '3px',
  skipToContent: true,
  
  // Color coding for ADHD
  colorCoding: {
    enabled: true,
    priority: {
      high: '#dc3545',
      medium: '#ffc107', 
      low: '#28a745',
      info: '#17a2b8'
    },
    status: {
      success: '#28a745',
      warning: '#ffc107',
      error: '#dc3545',
      info: '#17a2b8'
    }
  },
  
  // Cognitive load reduction
  simplifiedUI: false,
  showProgress: true,
  autoSave: true,
  confirmations: true,
  
  // Keyboard navigation
  keyboardNavigation: true,
  shortcuts: {
    'Alt+H': 'toggle-high-contrast',
    'Alt+M': 'toggle-reduced-motion',
    'Alt+1': 'navigate-dashboard',
    'Alt+2': 'navigate-security',
    'Alt+3': 'navigate-analytics',
    'Alt+4': 'navigate-plugins',
    'Alt+5': 'navigate-settings',
    'Alt+6': 'navigate-help',
    'Escape': 'close-modal'
  },
  
  // Screen reader support
  screenReader: {
    announcements: true,
    liveRegions: true,
    descriptions: true
  },
  
  // ADHD-specific features
  adhd: {
    timerReminders: true,
    progressVisuals: true,
    taskBreakdown: true,
    focusMode: false,
    distractionFilter: false,
    timeBlocking: false
  },
  
  // Theme preferences
  theme: {
    mode: 'auto', // light, dark, auto
    primaryColor: '#1976d2',
    accentColor: '#dc3545',
    spacing: 'comfortable' // compact, comfortable, spacious
  }
};

// Action types
const actionTypes = {
  TOGGLE_HIGH_CONTRAST: 'TOGGLE_HIGH_CONTRAST',
  TOGGLE_REDUCED_MOTION: 'TOGGLE_REDUCED_MOTION',
  SET_FONT_SIZE: 'SET_FONT_SIZE',
  SET_LINE_HEIGHT: 'SET_LINE_HEIGHT',
  SET_LETTER_SPACING: 'SET_LETTER_SPACING',
  TOGGLE_ENHANCED_FOCUS: 'TOGGLE_ENHANCED_FOCUS',
  TOGGLE_SIMPLIFIED_UI: 'TOGGLE_SIMPLIFIED_UI',
  TOGGLE_COLOR_CODING: 'TOGGLE_COLOR_CODING',
  UPDATE_SHORTCUTS: 'UPDATE_SHORTCUTS',
  TOGGLE_ADHD_FEATURE: 'TOGGLE_ADHD_FEATURE',
  SET_THEME: 'SET_THEME',
  RESET_PREFERENCES: 'RESET_PREFERENCES',
  LOAD_PREFERENCES: 'LOAD_PREFERENCES'
};

// Reducer for accessibility state
const accessibilityReducer = (state, action) => {
  switch (action.type) {
    case actionTypes.TOGGLE_HIGH_CONTRAST:
      return {
        ...state,
        highContrast: !state.highContrast
      };
      
    case actionTypes.TOGGLE_REDUCED_MOTION:
      return {
        ...state,
        reducedMotion: !state.reducedMotion
      };
      
    case actionTypes.SET_FONT_SIZE:
      return {
        ...state,
        fontSize: action.payload
      };
      
    case actionTypes.SET_LINE_HEIGHT:
      return {
        ...state,
        lineHeight: action.payload
      };
      
    case actionTypes.SET_LETTER_SPACING:
      return {
        ...state,
        letterSpacing: action.payload
      };
      
    case actionTypes.TOGGLE_ENHANCED_FOCUS:
      return {
        ...state,
        enhancedFocus: !state.enhancedFocus
      };
      
    case actionTypes.TOGGLE_SIMPLIFIED_UI:
      return {
        ...state,
        simplifiedUI: !state.simplifiedUI
      };
      
    case actionTypes.TOGGLE_COLOR_CODING:
      return {
        ...state,
        colorCoding: {
          ...state.colorCoding,
          enabled: !state.colorCoding.enabled
        }
      };
      
    case actionTypes.TOGGLE_ADHD_FEATURE:
      return {
        ...state,
        adhd: {
          ...state.adhd,
          [action.payload]: !state.adhd[action.payload]
        }
      };
      
    case actionTypes.SET_THEME:
      return {
        ...state,
        theme: {
          ...state.theme,
          ...action.payload
        }
      };
      
    case actionTypes.LOAD_PREFERENCES:
      return {
        ...state,
        ...action.payload
      };
      
    case actionTypes.RESET_PREFERENCES:
      return initialState;
      
    default:
      return state;
  }
};

// Create context
const AccessibilityContext = createContext();

// Provider component
export const AccessibilityProvider = ({ children }) => {
  const [state, dispatch] = useReducer(accessibilityReducer, initialState);

  // Load preferences from localStorage on mount
  useEffect(() => {
    const savedPreferences = localStorage.getItem('noxpanel-accessibility');
    if (savedPreferences) {
      try {
        const preferences = JSON.parse(savedPreferences);
        dispatch({ type: actionTypes.LOAD_PREFERENCES, payload: preferences });
      } catch (error) {
        console.warn('Failed to load accessibility preferences:', error);
      }
    }
  }, []);

  // Save preferences to localStorage when state changes
  useEffect(() => {
    localStorage.setItem('noxpanel-accessibility', JSON.stringify(state));
  }, [state]);

  // Apply CSS custom properties based on state
  useEffect(() => {
    const root = document.documentElement;
    
    // Font size mapping
    const fontSizeMap = {
      small: '14px',
      medium: '16px',
      large: '18px',
      'extra-large': '20px'
    };
    
    // Apply CSS custom properties
    root.style.setProperty('--accessibility-font-size', fontSizeMap[state.fontSize]);
    root.style.setProperty('--accessibility-line-height', state.lineHeight.toString());
    root.style.setProperty('--accessibility-letter-spacing', `${state.letterSpacing}px`);
    root.style.setProperty('--accessibility-focus-width', state.focusRingWidth);
    
    // High contrast mode
    if (state.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }
    
    // Reduced motion
    if (state.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }
    
    // Enhanced focus
    if (state.enhancedFocus) {
      root.classList.add('enhanced-focus');
    } else {
      root.classList.remove('enhanced-focus');
    }
    
    // Simplified UI
    if (state.simplifiedUI) {
      root.classList.add('simplified-ui');
    } else {
      root.classList.remove('simplified-ui');
    }
    
    // Color coding
    if (state.colorCoding.enabled) {
      Object.entries(state.colorCoding.priority).forEach(([key, value]) => {
        root.style.setProperty(`--color-priority-${key}`, value);
      });
      Object.entries(state.colorCoding.status).forEach(([key, value]) => {
        root.style.setProperty(`--color-status-${key}`, value);
      });
    }
    
  }, [state]);

  // Keyboard shortcuts handler
  useEffect(() => {
    const handleKeyboardShortcuts = (event) => {
      if (!state.keyboardNavigation) return;
      
      const shortcutKey = `${event.altKey ? 'Alt+' : ''}${event.ctrlKey ? 'Ctrl+' : ''}${event.key}`;
      const action = state.shortcuts[shortcutKey];
      
      if (action) {
        event.preventDefault();
        
        switch (action) {
          case 'toggle-high-contrast':
            dispatch({ type: actionTypes.TOGGLE_HIGH_CONTRAST });
            announceToScreenReader('High contrast mode toggled');
            break;
            
          case 'toggle-reduced-motion':
            dispatch({ type: actionTypes.TOGGLE_REDUCED_MOTION });
            announceToScreenReader('Reduced motion toggled');
            break;
            
          case 'navigate-dashboard':
            window.location.hash = '#/dashboard';
            announceToScreenReader('Navigated to dashboard');
            break;
            
          case 'navigate-security':
            window.location.hash = '#/security';
            announceToScreenReader('Navigated to security');
            break;
            
          case 'navigate-analytics':
            window.location.hash = '#/analytics';
            announceToScreenReader('Navigated to analytics');
            break;
            
          case 'navigate-plugins':
            window.location.hash = '#/plugins';
            announceToScreenReader('Navigated to plugins');
            break;
            
          case 'navigate-settings':
            window.location.hash = '#/settings';
            announceToScreenReader('Navigated to settings');
            break;
            
          case 'close-modal':
            // Emit custom event for modal closing
            window.dispatchEvent(new CustomEvent('close-modal'));
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyboardShortcuts);
    return () => document.removeEventListener('keydown', handleKeyboardShortcuts);
  }, [state.keyboardNavigation, state.shortcuts]);

  // Screen reader announcement function
  const announceToScreenReader = (message) => {
    if (!state.screenReader.announcements) return;
    
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  // Action creators
  const actions = {
    toggleHighContrast: () => dispatch({ type: actionTypes.TOGGLE_HIGH_CONTRAST }),
    toggleReducedMotion: () => dispatch({ type: actionTypes.TOGGLE_REDUCED_MOTION }),
    setFontSize: (size) => dispatch({ type: actionTypes.SET_FONT_SIZE, payload: size }),
    setLineHeight: (height) => dispatch({ type: actionTypes.SET_LINE_HEIGHT, payload: height }),
    setLetterSpacing: (spacing) => dispatch({ type: actionTypes.SET_LETTER_SPACING, payload: spacing }),
    toggleEnhancedFocus: () => dispatch({ type: actionTypes.TOGGLE_ENHANCED_FOCUS }),
    toggleSimplifiedUI: () => dispatch({ type: actionTypes.TOGGLE_SIMPLIFIED_UI }),
    toggleColorCoding: () => dispatch({ type: actionTypes.TOGGLE_COLOR_CODING }),
    toggleAdhdFeature: (feature) => dispatch({ type: actionTypes.TOGGLE_ADHD_FEATURE, payload: feature }),
    setTheme: (themeProps) => dispatch({ type: actionTypes.SET_THEME, payload: themeProps }),
    resetPreferences: () => dispatch({ type: actionTypes.RESET_PREFERENCES }),
    announceToScreenReader
  };

  const value = {
    ...state,
    ...actions
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
};

// Hook for using accessibility context
export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

// HOC for accessibility features
export const withAccessibility = (Component) => {
  return function AccessibilityEnhancedComponent(props) {
    const accessibility = useAccessibility();
    return <Component {...props} accessibility={accessibility} />;
  };
};

export default AccessibilityContext;
