"""
NoxSuite Security Platform - ML Module
======================================

This module provides AI/ML capabilities for intelligent automation,
anomaly detection, and AI-enhanced security auditing.

Modules:
- model_training: Train basic models on security logs
- anomaly_detection: Outlier detection on system metrics/logs  
- predictive_engine: Framework for risk scoring using ML algorithms

Requirements:
- TensorFlow for neural networks and model deployment
- PyTorch for dynamic AI modeling and NLP tasks
- Scikit-learn for classical ML algorithms and behavior analysis
- XGBoost/LightGBM for gradient boosting and anomaly scoring
- NLTK for natural language processing of logs and threat intelligence
- OpenCV for visual security analysis (optional)
- Pandas/NumPy for data wrangling and preprocessing
- H2O.ai for automated ML pipeline experimentation
"""

__version__ = "1.0.0"
__author__ = "NoxSuite Security Team"

# Import key ML components
try:
    from .model_training import SecurityModelTrainer
    from .anomaly_detection import AnomalyDetector
    from .predictive_engine import RiskScoreEngine
    
    __all__ = [
        'SecurityModelTrainer',
        'AnomalyDetector', 
        'RiskScoreEngine'
    ]
except ImportError as e:
    # Graceful handling if ML dependencies not installed
    print(f"Warning: ML dependencies not fully installed. {e}")
    __all__ = []