"""
Predictive Risk Scoring Engine
=============================

This module provides a framework for risk scoring using advanced machine learning
algorithms including Scikit-learn and XGBoost for predictive security analysis.

Features:
- User risk score calculation
- Threat likelihood prediction
- Security incident probability scoring
- Real-time risk assessment
- Historical risk trend analysis
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler, RobustScaler
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    import joblib
    
    # Try importing advanced ML libraries
    try:
        import xgboost as xgb
        XGBOOST_AVAILABLE = True
    except ImportError:
        XGBOOST_AVAILABLE = False
        
    try:
        import lightgbm as lgb
        LIGHTGBM_AVAILABLE = True
    except ImportError:
        LIGHTGBM_AVAILABLE = False
        
except ImportError as e:
    logging.warning(f"ML dependencies not available: {e}")
    np = pd = None


class RiskLevel(Enum):
    """Risk level enumeration."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskScore:
    """Data class for risk assessment results."""
    entity_id: str
    entity_type: str  # 'user', 'ip', 'session', 'system'
    risk_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    confidence: float  # Model confidence 0.0 to 1.0
    factors: Dict[str, float]  # Contributing factors
    timestamp: datetime
    prediction_horizon: str  # '1h', '24h', '7d', etc.
    recommendations: List[str]


class RiskScoreEngine:
    """
    Main class for predictive risk scoring in security systems.
    
    Provides comprehensive risk assessment using multiple ML algorithms
    and real-time scoring capabilities.
    """
    
    def __init__(self, model_dir: str = "./models", config_path: Optional[str] = None):
        """
        Initialize the Risk Score Engine.
        
        Args:
            model_dir: Directory to save/load trained models
            config_path: Path to configuration file (optional)
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.risk_history = {}
        
        # Default configuration
        self.config = {
            'risk_thresholds': {
                'minimal': 0.2,
                'low': 0.4,
                'medium': 0.6,
                'high': 0.8,
                'critical': 1.0
            },
            'model_types': ['xgboost', 'lightgbm', 'random_forest'],
            'feature_weights': {
                'login_frequency': 0.2,
                'failed_logins': 0.3,
                'unusual_hours': 0.1,
                'ip_reputation': 0.2,
                'privilege_escalation': 0.2
            },
            'prediction_horizons': ['1h', '6h', '24h', '7d'],
            'min_training_samples': 100
        }
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def calculate_user_risk_score(self, user_id: str, user_data: pd.DataFrame) -> RiskScore:
        """
        Calculate comprehensive risk score for a user.
        
        Args:
            user_id: User identifier
            user_data: Historical user activity data
            
        Returns:
            RiskScore object with detailed assessment
        """
        if pd is None:
            raise ImportError("Pandas not available")
        
        # Extract user features
        features = self._extract_user_features(user_data)
        
        # Calculate base risk score using ensemble of models
        risk_score = self._calculate_ensemble_risk_score(features, 'user')
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Calculate model confidence
        confidence = self._calculate_model_confidence(features, 'user')
        
        # Identify contributing factors
        factors = self._analyze_risk_factors(features, user_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_score, factors, 'user')
        
        risk_assessment = RiskScore(
            entity_id=user_id,
            entity_type='user',
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            factors=factors,
            timestamp=datetime.now(),
            prediction_horizon='24h',
            recommendations=recommendations
        )
        
        # Store in history
        self._store_risk_history(user_id, risk_assessment)
        
        return risk_assessment
    
    def calculate_session_risk_score(self, session_id: str, session_data: Dict[str, Any]) -> RiskScore:
        """
        Calculate risk score for an active session.
        
        Args:
            session_id: Session identifier
            session_data: Current session information
            
        Returns:
            RiskScore object for the session
        """
        # Extract session features
        features = self._extract_session_features(session_data)
        
        # Calculate risk score
        risk_score = self._calculate_session_risk(features)
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Analyze factors
        factors = self._analyze_session_factors(session_data)
        
        # Generate recommendations
        recommendations = self._generate_session_recommendations(risk_score, factors)
        
        return RiskScore(
            entity_id=session_id,
            entity_type='session',
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=0.8,  # Default confidence for session scoring
            factors=factors,
            timestamp=datetime.now(),
            prediction_horizon='1h',
            recommendations=recommendations
        )
    
    def calculate_ip_risk_score(self, ip_address: str, ip_data: pd.DataFrame) -> RiskScore:
        """
        Calculate risk score for an IP address.
        
        Args:
            ip_address: IP address to assess
            ip_data: Historical data for the IP
            
        Returns:
            RiskScore object for the IP
        """
        if pd is None:
            raise ImportError("Pandas not available")
        
        # Extract IP-based features
        features = self._extract_ip_features(ip_data)
        
        # Calculate risk score
        risk_score = self._calculate_ip_risk(features, ip_address)
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Analyze contributing factors
        factors = self._analyze_ip_factors(ip_data, ip_address)
        
        # Generate recommendations
        recommendations = self._generate_ip_recommendations(risk_score, factors)
        
        return RiskScore(
            entity_id=ip_address,
            entity_type='ip',
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=0.7,  # IP-based scoring typically has lower confidence
            factors=factors,
            timestamp=datetime.now(),
            prediction_horizon='6h',
            recommendations=recommendations
        )
    
    def train_risk_models(self, training_data: pd.DataFrame, target_column: str = 'risk_score') -> Dict[str, Any]:
        """
        Train risk scoring models on historical data.
        
        Args:
            training_data: Historical data with known risk scores
            target_column: Column containing risk scores (0.0 to 1.0)
            
        Returns:
            Training results and metrics
        """
        if pd is None:
            raise ImportError("Pandas not available")
        
        self.logger.info("Training risk scoring models...")
        
        # Prepare features and targets
        features = self._prepare_training_features(training_data)
        targets = training_data[target_column].values
        
        if len(features) < self.config['min_training_samples']:
            raise ValueError(f"Insufficient training data: {len(features)} < {self.config['min_training_samples']}")
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            features, targets, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['risk_scaler'] = scaler
        
        results = {}
        
        # Train multiple models
        if XGBOOST_AVAILABLE:
            results['xgboost'] = self._train_xgboost_model(X_train_scaled, y_train, X_test_scaled, y_test)
        
        if LIGHTGBM_AVAILABLE:
            results['lightgbm'] = self._train_lightgbm_model(X_train_scaled, y_train, X_test_scaled, y_test)
        
        # Always train Random Forest as fallback
        results['random_forest'] = self._train_random_forest_model(X_train_scaled, y_train, X_test_scaled, y_test)
        
        # Select best model
        best_model_name = min(results.keys(), key=lambda k: results[k]['mae'])
        self.best_model = best_model_name
        
        # Save models and scaler
        self._save_models_and_scaler()
        
        training_summary = {
            'total_samples': len(features),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_count': features.shape[1],
            'best_model': best_model_name,
            'model_results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Risk models trained successfully. Best model: {best_model_name}")
        return training_summary
    
    def _extract_user_features(self, user_data: pd.DataFrame) -> np.ndarray:
        """Extract features from user activity data."""
        if len(user_data) == 0:
            return np.array([[0] * 10])  # Return default features
        
        # Calculate user behavior features
        features = {
            'login_frequency': len(user_data) / max(1, (user_data['timestamp'].max() - user_data['timestamp'].min()).days or 1),
            'failed_login_ratio': (user_data['status'] == 'failed').mean() if 'status' in user_data.columns else 0,
            'unique_ips': user_data['ip_address'].nunique() if 'ip_address' in user_data.columns else 1,
            'unusual_hour_logins': ((pd.to_datetime(user_data['timestamp']).dt.hour < 6) | 
                                   (pd.to_datetime(user_data['timestamp']).dt.hour > 22)).mean() if 'timestamp' in user_data.columns else 0,
            'weekend_activity': (pd.to_datetime(user_data['timestamp']).dt.weekday >= 5).mean() if 'timestamp' in user_data.columns else 0,
            'session_duration_avg': user_data['session_duration'].mean() if 'session_duration' in user_data.columns else 30,
            'privilege_escalation_attempts': (user_data['action'] == 'privilege_escalation').sum() if 'action' in user_data.columns else 0,
            'data_access_volume': user_data['data_accessed'].sum() if 'data_accessed' in user_data.columns else 0,
            'external_ip_usage': (~user_data['ip_address'].str.startswith('192.168.')).mean() if 'ip_address' in user_data.columns else 0,
            'recent_activity_spike': 1 if len(user_data[user_data['timestamp'] > datetime.now() - timedelta(hours=1)]) > 10 else 0
        }
        
        return np.array(list(features.values())).reshape(1, -1)
    
    def _extract_session_features(self, session_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from current session data."""
        features = {
            'session_duration': session_data.get('duration_minutes', 0),
            'pages_accessed': session_data.get('pages_accessed', 0),
            'failed_attempts': session_data.get('failed_attempts', 0),
            'unusual_hour': 1 if datetime.now().hour < 6 or datetime.now().hour > 22 else 0,
            'external_ip': 1 if not session_data.get('ip_address', '').startswith('192.168.') else 0,
            'new_device': 1 if session_data.get('new_device', False) else 0,
            'suspicious_user_agent': 1 if 'bot' in session_data.get('user_agent', '').lower() else 0,
            'multiple_failed_logins': 1 if session_data.get('failed_login_count', 0) > 3 else 0,
            'privilege_requests': session_data.get('privilege_requests', 0),
            'data_download_volume': session_data.get('data_downloaded_mb', 0)
        }
        
        return np.array(list(features.values())).reshape(1, -1)
    
    def _extract_ip_features(self, ip_data: pd.DataFrame) -> np.ndarray:
        """Extract features from IP address activity data."""
        if len(ip_data) == 0:
            return np.array([[0] * 8])
        
        features = {
            'request_frequency': len(ip_data) / max(1, (ip_data['timestamp'].max() - ip_data['timestamp'].min()).days or 1),
            'unique_users': ip_data['user_id'].nunique() if 'user_id' in ip_data.columns else 1,
            'failed_request_ratio': (ip_data['status'] == 'failed').mean() if 'status' in ip_data.columns else 0,
            'geographic_anomaly': 0,  # Placeholder for geolocation analysis
            'blacklist_score': 0,  # Placeholder for IP reputation score
            'port_scan_indicators': ip_data['unique_ports'].nunique() if 'unique_ports' in ip_data.columns else 1,
            'unusual_protocols': (ip_data['protocol'] != 'HTTP').mean() if 'protocol' in ip_data.columns else 0,
            'data_volume': ip_data['bytes_transferred'].sum() if 'bytes_transferred' in ip_data.columns else 0
        }
        
        return np.array(list(features.values())).reshape(1, -1)
    
    def _calculate_ensemble_risk_score(self, features: np.ndarray, entity_type: str) -> float:
        """Calculate risk score using ensemble of models."""
        if not self.models:
            # Use rule-based scoring if no trained models
            return self._calculate_rule_based_risk_score(features, entity_type)
        
        scores = []
        weights = []
        
        for model_name, model in self.models.items():
            try:
                if 'risk_scaler' in self.scalers:
                    features_scaled = self.scalers['risk_scaler'].transform(features)
                else:
                    features_scaled = features
                
                score = model.predict(features_scaled)[0]
                scores.append(np.clip(score, 0.0, 1.0))  # Ensure score is in [0, 1]
                weights.append(1.0)  # Equal weights for now
                
            except Exception as e:
                self.logger.warning(f"Error using model {model_name}: {e}")
        
        if not scores:
            return self._calculate_rule_based_risk_score(features, entity_type)
        
        # Weighted average
        return np.average(scores, weights=weights)
    
    def _calculate_rule_based_risk_score(self, features: np.ndarray, entity_type: str) -> float:
        """Calculate risk score using rule-based approach."""
        if features.size == 0:
            return 0.3  # Default low-medium risk
        
        features_flat = features.flatten()
        
        if entity_type == 'user':
            # User risk scoring rules
            risk_score = 0.1  # Base risk
            
            # Login patterns
            if len(features_flat) > 1 and features_flat[1] > 0.3:  # High failed login ratio
                risk_score += 0.3
            
            if len(features_flat) > 2 and features_flat[2] > 5:  # Many unique IPs
                risk_score += 0.2
            
            if len(features_flat) > 3 and features_flat[3] > 0.2:  # Unusual hours
                risk_score += 0.2
            
            if len(features_flat) > 6 and features_flat[6] > 0:  # Privilege escalation
                risk_score += 0.3
                
        elif entity_type == 'session':
            # Session risk scoring rules
            risk_score = 0.1  # Base risk
            
            if len(features_flat) > 2 and features_flat[2] > 3:  # Failed attempts
                risk_score += 0.4
            
            if len(features_flat) > 4 and features_flat[4] > 0:  # External IP
                risk_score += 0.2
            
            if len(features_flat) > 5 and features_flat[5] > 0:  # New device
                risk_score += 0.1
                
        else:  # IP or other entity types
            risk_score = 0.2  # Default medium-low risk
        
        return np.clip(risk_score, 0.0, 1.0)
    
    def _calculate_session_risk(self, features: np.ndarray) -> float:
        """Calculate risk score specifically for sessions."""
        return self._calculate_ensemble_risk_score(features, 'session')
    
    def _calculate_ip_risk(self, features: np.ndarray, ip_address: str) -> float:
        """Calculate risk score specifically for IP addresses."""
        base_score = self._calculate_ensemble_risk_score(features, 'ip')
        
        # Add IP-specific adjustments
        if ip_address.startswith('192.168.') or ip_address.startswith('10.'):
            base_score *= 0.7  # Internal IPs get lower risk
        
        return np.clip(base_score, 0.0, 1.0)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from numerical score."""
        thresholds = self.config['risk_thresholds']
        
        if risk_score >= thresholds['critical']:
            return RiskLevel.CRITICAL
        elif risk_score >= thresholds['high']:
            return RiskLevel.HIGH
        elif risk_score >= thresholds['medium']:
            return RiskLevel.MEDIUM
        elif risk_score >= thresholds['low']:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _calculate_model_confidence(self, features: np.ndarray, entity_type: str) -> float:
        """Calculate confidence in the risk score prediction."""
        if not self.models:
            return 0.6  # Medium confidence for rule-based scoring
        
        # For now, return a confidence based on feature completeness
        feature_completeness = np.mean(features != 0) if features.size > 0 else 0.5
        return np.clip(feature_completeness * 0.8 + 0.2, 0.3, 0.95)
    
    def _analyze_risk_factors(self, features: np.ndarray, user_data: pd.DataFrame) -> Dict[str, float]:
        """Analyze contributing factors to the risk score."""
        factors = {}
        
        if features.size >= 10:  # Assuming 10 user features
            features_flat = features.flatten()
            factor_names = [
                'login_frequency', 'failed_login_ratio', 'unique_ips',
                'unusual_hour_logins', 'weekend_activity', 'session_duration_avg',
                'privilege_escalation_attempts', 'data_access_volume',
                'external_ip_usage', 'recent_activity_spike'
            ]
            
            for i, factor_name in enumerate(factor_names[:len(features_flat)]):
                factors[factor_name] = float(features_flat[i])
        
        return factors
    
    def _analyze_session_factors(self, session_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze contributing factors for session risk."""
        return {
            'session_duration': session_data.get('duration_minutes', 0) / 60.0,  # Normalize to hours
            'failed_attempts': min(session_data.get('failed_attempts', 0) / 10.0, 1.0),  # Normalize
            'unusual_timing': 1.0 if datetime.now().hour < 6 or datetime.now().hour > 22 else 0.0,
            'external_access': 1.0 if not session_data.get('ip_address', '').startswith('192.168.') else 0.0,
            'new_device': 1.0 if session_data.get('new_device', False) else 0.0
        }
    
    def _analyze_ip_factors(self, ip_data: pd.DataFrame, ip_address: str) -> Dict[str, float]:
        """Analyze contributing factors for IP risk."""
        if len(ip_data) == 0:
            return {'insufficient_data': 1.0}
        
        return {
            'request_volume': min(len(ip_data) / 100.0, 1.0),  # Normalize to 100 requests
            'failure_rate': (ip_data['status'] == 'failed').mean() if 'status' in ip_data.columns else 0,
            'user_diversity': min(ip_data['user_id'].nunique() / 10.0, 1.0) if 'user_id' in ip_data.columns else 0,
            'external_ip': 0.0 if ip_address.startswith(('192.168.', '10.', '172.16.')) else 1.0
        }
    
    def _generate_recommendations(self, risk_score: float, factors: Dict[str, float], entity_type: str) -> List[str]:
        """Generate security recommendations based on risk assessment."""
        recommendations = []
        
        if risk_score >= 0.8:
            recommendations.append("Immediate investigation required")
            recommendations.append("Consider temporary access restrictions")
        
        if risk_score >= 0.6:
            recommendations.append("Increase monitoring frequency")
            recommendations.append("Require additional authentication")
        
        # Factor-specific recommendations
        if factors.get('failed_login_ratio', 0) > 0.3:
            recommendations.append("Investigate repeated login failures")
        
        if factors.get('unusual_hour_logins', 0) > 0.5:
            recommendations.append("Review after-hours access patterns")
        
        if factors.get('privilege_escalation_attempts', 0) > 0:
            recommendations.append("Review privilege escalation attempts")
        
        if factors.get('external_ip_usage', 0) > 0.5:
            recommendations.append("Verify external IP access legitimacy")
        
        if not recommendations:
            recommendations.append("Continue standard monitoring")
        
        return recommendations
    
    def _generate_session_recommendations(self, risk_score: float, factors: Dict[str, float]) -> List[str]:
        """Generate session-specific recommendations."""
        recommendations = []
        
        if risk_score >= 0.7:
            recommendations.append("Consider session termination")
            recommendations.append("Require re-authentication")
        
        if factors.get('failed_attempts', 0) > 0.3:
            recommendations.append("Monitor for brute force attempts")
        
        if factors.get('new_device', 0) > 0:
            recommendations.append("Verify device identity")
        
        if factors.get('external_access', 0) > 0:
            recommendations.append("Confirm external access authorization")
        
        return recommendations or ["Continue session monitoring"]
    
    def _generate_ip_recommendations(self, risk_score: float, factors: Dict[str, float]) -> List[str]:
        """Generate IP-specific recommendations."""
        recommendations = []
        
        if risk_score >= 0.8:
            recommendations.append("Consider IP blocking")
            recommendations.append("Investigate source of traffic")
        
        if factors.get('failure_rate', 0) > 0.5:
            recommendations.append("Monitor for attack patterns")
        
        if factors.get('external_ip', 0) > 0:
            recommendations.append("Check IP reputation databases")
        
        return recommendations or ["Continue IP monitoring"]
    
    def _prepare_training_features(self, training_data: pd.DataFrame) -> np.ndarray:
        """Prepare features from training data."""
        # This is a simplified version - in practice, you'd extract the same features
        # used in the scoring functions
        feature_columns = [col for col in training_data.columns if col not in ['risk_score', 'timestamp', 'entity_id']]
        return training_data[feature_columns].fillna(0).values
    
    def _train_xgboost_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                           X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Train XGBoost model for risk scoring."""
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        self.models['xgboost'] = model
        
        # Evaluate
        y_pred = model.predict(X_test)
        
        return {
            'mae': mean_absolute_error(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
    
    def _train_lightgbm_model(self, X_train: np.ndarray, y_train: np.ndarray,
                            X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Train LightGBM model for risk scoring."""
        model = lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )
        
        model.fit(X_train, y_train)
        self.models['lightgbm'] = model
        
        # Evaluate
        y_pred = model.predict(X_test)
        
        return {
            'mae': mean_absolute_error(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
    
    def _train_random_forest_model(self, X_train: np.ndarray, y_train: np.ndarray,
                                 X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Train Random Forest model for risk scoring."""
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        self.models['random_forest'] = model
        
        # Evaluate
        y_pred = model.predict(X_test)
        
        return {
            'mae': mean_absolute_error(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
    
    def _save_models_and_scaler(self) -> None:
        """Save trained models and scaler to disk."""
        for model_name, model in self.models.items():
            model_path = self.model_dir / f"risk_{model_name}.pkl"
            joblib.dump(model, model_path)
            
        for scaler_name, scaler in self.scalers.items():
            scaler_path = self.model_dir / f"risk_{scaler_name}.pkl"
            joblib.dump(scaler, scaler_path)
    
    def _store_risk_history(self, entity_id: str, risk_score: RiskScore) -> None:
        """Store risk assessment in history."""
        if entity_id not in self.risk_history:
            self.risk_history[entity_id] = []
        
        self.risk_history[entity_id].append({
            'timestamp': risk_score.timestamp,
            'risk_score': risk_score.risk_score,
            'risk_level': risk_score.risk_level.value,
            'confidence': risk_score.confidence
        })
        
        # Keep only recent history (last 100 entries)
        if len(self.risk_history[entity_id]) > 100:
            self.risk_history[entity_id] = self.risk_history[entity_id][-100:]
    
    def _load_config(self, config_path: str) -> None:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.config.update(config)
            self.logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    def get_risk_trends(self, entity_id: str, days: int = 7) -> Dict[str, Any]:
        """Get risk trends for an entity over time."""
        if entity_id not in self.risk_history:
            return {'error': 'No history available'}
        
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_history = [
            entry for entry in self.risk_history[entity_id]
            if entry['timestamp'] >= cutoff_time
        ]
        
        if not recent_history:
            return {'error': 'No recent history available'}
        
        scores = [entry['risk_score'] for entry in recent_history]
        
        return {
            'entity_id': entity_id,
            'period_days': days,
            'total_assessments': len(recent_history),
            'average_risk_score': np.mean(scores),
            'max_risk_score': max(scores),
            'min_risk_score': min(scores),
            'risk_trend': 'increasing' if scores[-1] > scores[0] else 'decreasing',
            'latest_assessment': recent_history[-1]
        }


# Example usage and testing functions
def create_sample_training_data(n_samples: int = 500) -> pd.DataFrame:
    """Create sample training data for risk models."""
    if pd is None or np is None:
        raise ImportError("Pandas and NumPy required for sample data")
    
    np.random.seed(42)
    
    # Generate synthetic features
    data = {
        'login_frequency': np.random.exponential(2, n_samples),
        'failed_login_ratio': np.random.beta(1, 4, n_samples),
        'unique_ips': np.random.poisson(2, n_samples),
        'unusual_hour_logins': np.random.beta(1, 9, n_samples),
        'weekend_activity': np.random.beta(1, 3, n_samples),
        'session_duration_avg': np.random.normal(30, 10, n_samples),
        'privilege_escalation_attempts': np.random.poisson(0.1, n_samples),
        'data_access_volume': np.random.exponential(100, n_samples),
        'external_ip_usage': np.random.beta(1, 9, n_samples),
        'recent_activity_spike': np.random.binomial(1, 0.1, n_samples)
    }
    
    # Create synthetic risk scores based on features
    risk_scores = []
    for i in range(n_samples):
        risk = 0.1  # Base risk
        risk += data['failed_login_ratio'][i] * 0.4
        risk += min(data['unique_ips'][i] / 10, 0.3)
        risk += data['unusual_hour_logins'][i] * 0.2
        risk += data['privilege_escalation_attempts'][i] * 0.3
        risk += data['external_ip_usage'][i] * 0.2
        risk += data['recent_activity_spike'][i] * 0.2
        
        # Add some noise
        risk += np.random.normal(0, 0.05)
        risk_scores.append(np.clip(risk, 0.0, 1.0))
    
    data['risk_score'] = risk_scores
    data['timestamp'] = pd.date_range('2024-01-01', periods=n_samples, freq='H')
    data['entity_id'] = [f'user_{i//10}' for i in range(n_samples)]  # Multiple records per user
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    # Example usage
    try:
        # Create engine
        engine = RiskScoreEngine()
        
        # Create sample training data
        training_data = create_sample_training_data(500)
        print("Sample training data created:")
        print(training_data.head())
        
        # Train models
        training_results = engine.train_risk_models(training_data)
        print("\nTraining Results:")
        print(json.dumps(training_results, indent=2, default=str))
        
        # Test user risk scoring
        sample_user_data = training_data[training_data['entity_id'] == 'user_5'].copy()
        risk_score = engine.calculate_user_risk_score('user_5', sample_user_data)
        
        print(f"\nUser Risk Assessment:")
        print(f"User ID: {risk_score.entity_id}")
        print(f"Risk Score: {risk_score.risk_score:.3f}")
        print(f"Risk Level: {risk_score.risk_level.value}")
        print(f"Confidence: {risk_score.confidence:.3f}")
        print(f"Recommendations: {risk_score.recommendations}")
        
        # Test session risk scoring
        sample_session = {
            'duration_minutes': 45,
            'pages_accessed': 12,
            'failed_attempts': 1,
            'ip_address': '192.168.1.100',
            'new_device': False,
            'user_agent': 'Mozilla/5.0...'
        }
        
        session_risk = engine.calculate_session_risk_score('session_123', sample_session)
        print(f"\nSession Risk Assessment:")
        print(f"Session ID: {session_risk.entity_id}")
        print(f"Risk Score: {session_risk.risk_score:.3f}")
        print(f"Risk Level: {session_risk.risk_level.value}")
        
    except ImportError as e:
        print(f"Please install required ML dependencies: {e}")