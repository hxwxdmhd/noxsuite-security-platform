"""
Security Model Training Module
=============================

This module provides functionality to train basic machine learning models
on security logs and system metrics for predictive security analysis.

Features:
- Log-based anomaly detection model training
- User behavior analysis models
- Threat pattern recognition
- Model versioning and persistence
"""

import os
import json
import pickle
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import classification_report, confusion_matrix
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
    # Create dummy classes for graceful degradation
    np = pd = None


class SecurityModelTrainer:
    """
    Main class for training security-focused machine learning models.
    
    Supports training models for:
    - Login anomaly detection
    - Suspicious access pattern recognition
    - Risk scoring for user activities
    - Threat intelligence classification
    """
    
    def __init__(self, model_dir: str = "./models"):
        """
        Initialize the Security Model Trainer.
        
        Args:
            model_dir: Directory to save trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def prepare_security_data(self, log_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare security log data for model training.
        
        Args:
            log_data: Raw security log data
            
        Returns:
            Tuple of (features, labels)
        """
        if pd is None:
            raise ImportError("Pandas not available")
            
        # Example feature engineering for security logs
        features = pd.DataFrame()
        
        # Time-based features
        if 'timestamp' in log_data.columns:
            log_data['timestamp'] = pd.to_datetime(log_data['timestamp'])
            features['hour'] = log_data['timestamp'].dt.hour
            features['day_of_week'] = log_data['timestamp'].dt.dayofweek
            features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # User behavior features
        if 'user_id' in log_data.columns:
            user_stats = log_data.groupby('user_id').agg({
                'timestamp': 'count',
                'ip_address': 'nunique'
            }).rename(columns={'timestamp': 'login_frequency', 'ip_address': 'unique_ips'})
            features = features.join(user_stats, on='user_id', how='left')
        
        # Network features
        if 'ip_address' in log_data.columns:
            features['is_internal_ip'] = log_data['ip_address'].str.startswith('192.168.').astype(int)
        
        # Status and outcome features
        if 'status' in log_data.columns:
            if 'status_encoded' not in self.encoders:
                self.encoders['status_encoded'] = LabelEncoder()
                features['status_encoded'] = self.encoders['status_encoded'].fit_transform(log_data['status'])
            else:
                features['status_encoded'] = self.encoders['status_encoded'].transform(log_data['status'])
        
        # Create labels (1 for suspicious, 0 for normal)
        labels = pd.Series([0] * len(log_data), name='is_suspicious')
        if 'failed_login' in log_data.columns:
            labels = log_data['failed_login'].astype(int)
        
        return features.fillna(0), labels
    
    def train_anomaly_detector(self, log_data: pd.DataFrame, model_name: str = "login_anomaly") -> Dict[str, Any]:
        """
        Train an anomaly detection model for security logs.
        
        Args:
            log_data: Security log data
            model_name: Name for the trained model
            
        Returns:
            Training results and metrics
        """
        self.logger.info(f"Training anomaly detection model: {model_name}")
        
        # Prepare data
        features, _ = self.prepare_security_data(log_data)
        
        # Scale features
        scaler_name = f"{model_name}_scaler"
        self.scalers[scaler_name] = StandardScaler()
        features_scaled = self.scalers[scaler_name].fit_transform(features)
        
        # Train Isolation Forest for anomaly detection
        model = IsolationForest(
            contamination=0.1,  # Assume 10% anomalies
            random_state=42,
            n_estimators=100
        )
        
        model.fit(features_scaled)
        self.models[model_name] = model
        
        # Calculate anomaly scores
        anomaly_scores = model.decision_function(features_scaled)
        anomaly_predictions = model.predict(features_scaled)
        
        # Save model and scaler
        self._save_model(model_name, model)
        self._save_scaler(scaler_name, self.scalers[scaler_name])
        
        results = {
            'model_name': model_name,
            'model_type': 'IsolationForest',
            'anomaly_ratio': (anomaly_predictions == -1).mean(),
            'feature_count': features.shape[1],
            'training_samples': len(features),
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Anomaly detection model trained: {results}")
        return results
    
    def train_classification_model(self, log_data: pd.DataFrame, model_name: str = "threat_classifier") -> Dict[str, Any]:
        """
        Train a classification model for threat detection.
        
        Args:
            log_data: Labeled security log data
            model_name: Name for the trained model
            
        Returns:
            Training results and metrics
        """
        self.logger.info(f"Training classification model: {model_name}")
        
        # Prepare data
        features, labels = self.prepare_security_data(log_data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Scale features
        scaler_name = f"{model_name}_scaler"
        self.scalers[scaler_name] = StandardScaler()
        X_train_scaled = self.scalers[scaler_name].fit_transform(X_train)
        X_test_scaled = self.scalers[scaler_name].transform(X_test)
        
        # Choose best available model
        if XGBOOST_AVAILABLE:
            model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
        elif LIGHTGBM_AVAILABLE:
            model = lgb.LGBMClassifier(random_state=42, verbose=-1)
        else:
            model = RandomForestClassifier(random_state=42, n_estimators=100)
        
        # Train model
        model.fit(X_train_scaled, y_train)
        self.models[model_name] = model
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        classification_rep = classification_report(y_test, y_pred, output_dict=True)
        
        # Save model and scaler
        self._save_model(model_name, model)
        self._save_scaler(scaler_name, self.scalers[scaler_name])
        
        results = {
            'model_name': model_name,
            'model_type': type(model).__name__,
            'accuracy': classification_rep['accuracy'],
            'precision': classification_rep['weighted avg']['precision'],
            'recall': classification_rep['weighted avg']['recall'],
            'f1_score': classification_rep['weighted avg']['f1-score'],
            'feature_count': features.shape[1],
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Classification model trained: {results}")
        return results
    
    def _save_model(self, model_name: str, model: Any) -> None:
        """Save a trained model to disk."""
        model_path = self.model_dir / f"{model_name}.pkl"
        joblib.dump(model, model_path)
        self.logger.info(f"Model saved: {model_path}")
    
    def _save_scaler(self, scaler_name: str, scaler: Any) -> None:
        """Save a scaler to disk."""
        scaler_path = self.model_dir / f"{scaler_name}.pkl"
        joblib.dump(scaler, scaler_path)
        self.logger.info(f"Scaler saved: {scaler_path}")
    
    def load_model(self, model_name: str) -> Any:
        """Load a previously trained model."""
        model_path = self.model_dir / f"{model_name}.pkl"
        if model_path.exists():
            model = joblib.load(model_path)
            self.models[model_name] = model
            return model
        else:
            raise FileNotFoundError(f"Model not found: {model_path}")
    
    def list_models(self) -> List[str]:
        """List all available trained models."""
        model_files = list(self.model_dir.glob("*.pkl"))
        return [f.stem for f in model_files if not f.stem.endswith('_scaler')]


# Example usage and testing functions
def create_sample_security_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Create sample security log data for testing.
    
    Args:
        n_samples: Number of sample records to generate
        
    Returns:
        Sample security log DataFrame
    """
    if pd is None or np is None:
        raise ImportError("Pandas and NumPy required for sample data")
    
    np.random.seed(42)
    
    # Generate sample data
    data = {
        'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='H'),
        'user_id': np.random.choice(['user1', 'user2', 'user3', 'admin', 'guest'], n_samples),
        'ip_address': np.random.choice(['192.168.1.10', '192.168.1.20', '10.0.0.5', '203.0.113.1'], n_samples),
        'status': np.random.choice(['success', 'failed', 'blocked'], n_samples, p=[0.7, 0.2, 0.1]),
        'failed_login': np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    }
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    # Example usage
    try:
        # Create trainer
        trainer = SecurityModelTrainer()
        
        # Generate sample data
        sample_data = create_sample_security_data(1000)
        print("Sample data created:")
        print(sample_data.head())
        
        # Train anomaly detection model
        anomaly_results = trainer.train_anomaly_detector(sample_data)
        print("\nAnomaly Detection Results:")
        print(json.dumps(anomaly_results, indent=2))
        
        # Train classification model
        classification_results = trainer.train_classification_model(sample_data)
        print("\nClassification Results:")
        print(json.dumps(classification_results, indent=2))
        
        # List trained models
        models = trainer.list_models()
        print(f"\nTrained models: {models}")
        
    except ImportError as e:
        print(f"Please install required ML dependencies: {e}")