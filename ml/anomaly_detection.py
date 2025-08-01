"""
Anomaly Detection Module
=======================

This module provides real-time anomaly detection capabilities for security
monitoring, focusing on outlier detection in system metrics and log patterns.

Features:
- Real-time anomaly detection on login patterns
- System metrics anomaly monitoring
- Network traffic anomaly detection
- Behavioral analysis for user activities
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from dataclasses import dataclass

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.cluster import DBSCAN
    import joblib
    
    # Try importing advanced libraries
    try:
        import tensorflow as tf
        TENSORFLOW_AVAILABLE = True
    except ImportError:
        TENSORFLOW_AVAILABLE = False
        
    try:
        import torch
        import torch.nn as nn
        PYTORCH_AVAILABLE = True
    except ImportError:
        PYTORCH_AVAILABLE = False
        
except ImportError as e:
    logging.warning(f"ML dependencies not available: {e}")
    np = pd = None


@dataclass
class AnomalyAlert:
    """Data class for anomaly detection alerts."""
    timestamp: datetime
    anomaly_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    score: float
    description: str
    affected_entity: str
    raw_data: Dict[str, Any]


class AnomalyDetector:
    """
    Main class for real-time anomaly detection in security systems.
    
    Provides multiple detection algorithms and real-time monitoring
    capabilities for various security metrics and logs.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Anomaly Detector.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.models = {}
        self.scalers = {}
        self.baseline_stats = {}
        self.alert_history = []
        
        # Default configuration
        self.config = {
            'contamination_rate': 0.1,
            'min_samples_for_training': 100,
            'alert_threshold': 0.8,
            'severity_thresholds': {
                'critical': 0.9,
                'high': 0.7,
                'medium': 0.5,
                'low': 0.3
            }
        }
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def detect_login_anomalies(self, login_data: pd.DataFrame) -> List[AnomalyAlert]:
        """
        Detect anomalies in user login patterns.
        
        Args:
            login_data: DataFrame with login information
            
        Returns:
            List of anomaly alerts
        """
        if pd is None:
            raise ImportError("Pandas not available")
            
        alerts = []
        
        # Prepare login features
        features = self._extract_login_features(login_data)
        
        if len(features) < self.config['min_samples_for_training']:
            self.logger.warning("Insufficient data for anomaly detection")
            return alerts
        
        # Use or train anomaly detection model
        model_name = 'login_anomaly_detector'
        if model_name not in self.models:
            self._train_login_anomaly_model(features, model_name)
        
        # Detect anomalies
        anomaly_scores = self.models[model_name].decision_function(features)
        anomaly_predictions = self.models[model_name].predict(features)
        
        # Generate alerts for detected anomalies
        for idx, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
            if prediction == -1:  # Anomaly detected
                severity = self._calculate_severity(abs(score))
                
                alert = AnomalyAlert(
                    timestamp=datetime.now(),
                    anomaly_type='login_pattern',
                    severity=severity,
                    score=abs(score),
                    description=f"Unusual login pattern detected for user",
                    affected_entity=str(login_data.iloc[idx].get('user_id', 'unknown')),
                    raw_data=login_data.iloc[idx].to_dict()
                )
                alerts.append(alert)
        
        self.alert_history.extend(alerts)
        return alerts
    
    def detect_system_metric_anomalies(self, metrics: Dict[str, float]) -> List[AnomalyAlert]:
        """
        Detect anomalies in system metrics (CPU, memory, network, etc.).
        
        Args:
            metrics: Dictionary of system metrics
            
        Returns:
            List of anomaly alerts
        """
        alerts = []
        current_time = datetime.now()
        
        for metric_name, value in metrics.items():
            # Update baseline statistics
            self._update_baseline_stats(metric_name, value)
            
            # Check for statistical anomalies
            if self._is_statistical_anomaly(metric_name, value):
                severity = self._calculate_metric_severity(metric_name, value)
                
                alert = AnomalyAlert(
                    timestamp=current_time,
                    anomaly_type='system_metric',
                    severity=severity,
                    score=self._calculate_metric_score(metric_name, value),
                    description=f"Anomalous {metric_name} value detected: {value}",
                    affected_entity='system',
                    raw_data={'metric': metric_name, 'value': value}
                )
                alerts.append(alert)
        
        self.alert_history.extend(alerts)
        return alerts
    
    def detect_network_anomalies(self, network_data: pd.DataFrame) -> List[AnomalyAlert]:
        """
        Detect anomalies in network traffic patterns.
        
        Args:
            network_data: DataFrame with network traffic data
            
        Returns:
            List of anomaly alerts
        """
        if pd is None:
            raise ImportError("Pandas not available")
            
        alerts = []
        
        # Extract network features
        features = self._extract_network_features(network_data)
        
        if len(features) < self.config['min_samples_for_training']:
            return alerts
        
        # Use clustering-based anomaly detection
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        clusters = dbscan.fit_predict(features)
        
        # Identify outliers (cluster label -1)
        outliers = np.where(clusters == -1)[0]
        
        for idx in outliers:
            alert = AnomalyAlert(
                timestamp=datetime.now(),
                anomaly_type='network_traffic',
                severity='medium',
                score=0.8,  # Default score for clustering-based detection
                description="Unusual network traffic pattern detected",
                affected_entity=str(network_data.iloc[idx].get('source_ip', 'unknown')),
                raw_data=network_data.iloc[idx].to_dict()
            )
            alerts.append(alert)
        
        self.alert_history.extend(alerts)
        return alerts
    
    def detect_behavioral_anomalies(self, user_behavior: pd.DataFrame) -> List[AnomalyAlert]:
        """
        Detect anomalies in user behavior patterns.
        
        Args:
            user_behavior: DataFrame with user behavior data
            
        Returns:
            List of anomaly alerts
        """
        if pd is None:
            raise ImportError("Pandas not available")
            
        alerts = []
        
        # Group by user and analyze behavior patterns
        for user_id, user_data in user_behavior.groupby('user_id'):
            # Extract behavioral features
            features = self._extract_behavioral_features(user_data)
            
            if len(features) < 10:  # Need minimum data for behavior analysis
                continue
            
            # Use temporal pattern analysis
            anomalies = self._detect_temporal_anomalies(features)
            
            for anomaly_idx in anomalies:
                alert = AnomalyAlert(
                    timestamp=datetime.now(),
                    anomaly_type='user_behavior',
                    severity='medium',
                    score=0.7,
                    description=f"Unusual behavior pattern for user {user_id}",
                    affected_entity=str(user_id),
                    raw_data=user_data.iloc[anomaly_idx].to_dict()
                )
                alerts.append(alert)
        
        self.alert_history.extend(alerts)
        return alerts
    
    def _extract_login_features(self, login_data: pd.DataFrame) -> np.ndarray:
        """Extract features from login data for anomaly detection."""
        features = []
        
        for _, row in login_data.iterrows():
            feature_vector = [
                # Time-based features
                pd.to_datetime(row.get('timestamp', datetime.now())).hour,
                pd.to_datetime(row.get('timestamp', datetime.now())).weekday(),
                
                # Login frequency (mock calculation)
                hash(str(row.get('user_id', ''))) % 100,
                
                # IP-based features
                1 if str(row.get('ip_address', '')).startswith('192.168.') else 0,
                
                # Status features
                1 if row.get('status', '') == 'failed' else 0,
            ]
            features.append(feature_vector)
        
        features_array = np.array(features)
        
        # Scale features
        scaler_name = 'login_scaler'
        if scaler_name not in self.scalers:
            self.scalers[scaler_name] = StandardScaler()
            return self.scalers[scaler_name].fit_transform(features_array)
        else:
            return self.scalers[scaler_name].transform(features_array)
    
    def _extract_network_features(self, network_data: pd.DataFrame) -> np.ndarray:
        """Extract features from network data for anomaly detection."""
        features = []
        
        for _, row in network_data.iterrows():
            feature_vector = [
                row.get('bytes_sent', 0),
                row.get('bytes_received', 0),
                row.get('packets_sent', 0),
                row.get('packets_received', 0),
                row.get('connection_duration', 0),
                hash(str(row.get('source_ip', ''))) % 1000,
                hash(str(row.get('dest_ip', ''))) % 1000,
            ]
            features.append(feature_vector)
        
        features_array = np.array(features)
        
        # Scale features
        scaler_name = 'network_scaler'
        if scaler_name not in self.scalers:
            self.scalers[scaler_name] = StandardScaler()
            return self.scalers[scaler_name].fit_transform(features_array)
        else:
            return self.scalers[scaler_name].transform(features_array)
    
    def _extract_behavioral_features(self, user_data: pd.DataFrame) -> np.ndarray:
        """Extract behavioral features from user activity data."""
        if len(user_data) == 0:
            return np.array([])
        
        # Calculate temporal patterns
        timestamps = pd.to_datetime(user_data.get('timestamp', []))
        hours = timestamps.dt.hour.values if len(timestamps) > 0 else [12]
        
        # Calculate session patterns
        session_durations = user_data.get('session_duration', [30]).values
        page_views = user_data.get('page_views', [5]).values
        
        features = np.column_stack([
            hours,
            session_durations,
            page_views
        ])
        
        return features
    
    def _train_login_anomaly_model(self, features: np.ndarray, model_name: str) -> None:
        """Train an anomaly detection model for login patterns."""
        model = IsolationForest(
            contamination=self.config['contamination_rate'],
            random_state=42,
            n_estimators=100
        )
        
        model.fit(features)
        self.models[model_name] = model
        
        self.logger.info(f"Trained anomaly detection model: {model_name}")
    
    def _update_baseline_stats(self, metric_name: str, value: float) -> None:
        """Update baseline statistics for a metric."""
        if metric_name not in self.baseline_stats:
            self.baseline_stats[metric_name] = {
                'values': [],
                'mean': 0,
                'std': 0,
                'min': value,
                'max': value
            }
        
        stats = self.baseline_stats[metric_name]
        stats['values'].append(value)
        
        # Keep only recent values (last 1000)
        if len(stats['values']) > 1000:
            stats['values'] = stats['values'][-1000:]
        
        # Update statistics
        values = np.array(stats['values'])
        stats['mean'] = np.mean(values)
        stats['std'] = np.std(values)
        stats['min'] = np.min(values)
        stats['max'] = np.max(values)
    
    def _is_statistical_anomaly(self, metric_name: str, value: float) -> bool:
        """Check if a metric value is a statistical anomaly."""
        if metric_name not in self.baseline_stats:
            return False
        
        stats = self.baseline_stats[metric_name]
        if stats['std'] == 0:
            return False
        
        # Use z-score threshold of 3 (3 standard deviations)
        z_score = abs(value - stats['mean']) / stats['std']
        return z_score > 3
    
    def _calculate_severity(self, score: float) -> str:
        """Calculate alert severity based on anomaly score."""
        thresholds = self.config['severity_thresholds']
        
        if score >= thresholds['critical']:
            return 'critical'
        elif score >= thresholds['high']:
            return 'high'
        elif score >= thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_metric_severity(self, metric_name: str, value: float) -> str:
        """Calculate severity for system metric anomalies."""
        if metric_name not in self.baseline_stats:
            return 'low'
        
        stats = self.baseline_stats[metric_name]
        if stats['std'] == 0:
            return 'low'
        
        z_score = abs(value - stats['mean']) / stats['std']
        
        if z_score >= 5:
            return 'critical'
        elif z_score >= 4:
            return 'high'
        elif z_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_metric_score(self, metric_name: str, value: float) -> float:
        """Calculate anomaly score for a metric value."""
        if metric_name not in self.baseline_stats:
            return 0.5
        
        stats = self.baseline_stats[metric_name]
        if stats['std'] == 0:
            return 0.0
        
        z_score = abs(value - stats['mean']) / stats['std']
        # Normalize z-score to 0-1 range
        return min(z_score / 5, 1.0)
    
    def _detect_temporal_anomalies(self, features: np.ndarray) -> List[int]:
        """Detect temporal anomalies in user behavior."""
        if len(features) < 5:
            return []
        
        # Simple temporal anomaly detection using sliding window
        anomalies = []
        window_size = min(5, len(features) // 2)
        
        for i in range(window_size, len(features)):
            current_window = features[i-window_size:i]
            current_value = features[i]
            
            # Check if current value deviates significantly from window mean
            window_mean = np.mean(current_window, axis=0)
            current_deviation = np.linalg.norm(current_value - window_mean)
            window_std = np.std(np.linalg.norm(current_window - window_mean, axis=1))
            
            if window_std > 0 and current_deviation > 2 * window_std:
                anomalies.append(i)
        
        return anomalies
    
    def _load_config(self, config_path: str) -> None:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.config.update(config)
            self.logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of alerts from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [alert for alert in self.alert_history 
                        if alert.timestamp >= cutoff_time]
        
        summary = {
            'total_alerts': len(recent_alerts),
            'by_severity': {},
            'by_type': {},
            'latest_alert': None
        }
        
        for alert in recent_alerts:
            # Count by severity
            summary['by_severity'][alert.severity] = summary['by_severity'].get(alert.severity, 0) + 1
            
            # Count by type
            summary['by_type'][alert.anomaly_type] = summary['by_type'].get(alert.anomaly_type, 0) + 1
        
        if recent_alerts:
            latest = max(recent_alerts, key=lambda x: x.timestamp)
            summary['latest_alert'] = {
                'timestamp': latest.timestamp.isoformat(),
                'type': latest.anomaly_type,
                'severity': latest.severity,
                'description': latest.description
            }
        
        return summary


# Example usage and testing functions
def create_sample_system_metrics() -> Dict[str, float]:
    """Create sample system metrics for testing."""
    if np is None:
        raise ImportError("NumPy required for sample data")
    
    return {
        'cpu_usage': np.random.normal(50, 10),  # Normal: 50% ± 10%
        'memory_usage': np.random.normal(60, 15),  # Normal: 60% ± 15%
        'disk_usage': np.random.normal(40, 5),  # Normal: 40% ± 5%
        'network_throughput': np.random.exponential(100),  # Exponential distribution
        'active_connections': np.random.poisson(20)  # Poisson distribution
    }


if __name__ == "__main__":
    # Example usage
    try:
        # Create detector
        detector = AnomalyDetector()
        
        # Test system metrics anomaly detection
        print("Testing system metrics anomaly detection...")
        for i in range(50):
            metrics = create_sample_system_metrics()
            alerts = detector.detect_system_metric_anomalies(metrics)
            
            if alerts:
                print(f"Alerts detected: {len(alerts)}")
                for alert in alerts:
                    print(f"  - {alert.severity.upper()}: {alert.description}")
        
        # Get alert summary
        summary = detector.get_alert_summary()
        print(f"\nAlert Summary: {json.dumps(summary, indent=2)}")
        
    except ImportError as e:
        print(f"Please install required ML dependencies: {e}")