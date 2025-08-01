#!/usr/bin/env python3
"""
NoxSuite AI/ML Integration Validation Script
===========================================

This script validates that all AI/ML components are working correctly.
"""

import sys
import os
import traceback
from datetime import datetime

def test_basic_imports():
    """Test that all required libraries can be imported."""
    print("🔍 Testing basic imports...")
    
    try:
        import numpy as np
        print("  ✅ NumPy available")
    except ImportError as e:
        print(f"  ❌ NumPy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("  ✅ Pandas available")
    except ImportError as e:
        print(f"  ❌ Pandas import failed: {e}")
        return False
    
    try:
        from sklearn.ensemble import IsolationForest
        print("  ✅ Scikit-learn available")
    except ImportError as e:
        print(f"  ❌ Scikit-learn import failed: {e}")
        return False
    
    # Test optional libraries
    try:
        import tensorflow as tf
        print("  ✅ TensorFlow available")
    except ImportError:
        print("  ⚠️  TensorFlow not available (optional)")
    
    try:
        import torch
        print("  ✅ PyTorch available")
    except ImportError:
        print("  ⚠️  PyTorch not available (optional)")
    
    try:
        import xgboost as xgb
        print("  ✅ XGBoost available")
    except ImportError:
        print("  ⚠️  XGBoost not available (optional)")
    
    try:
        import lightgbm as lgb
        print("  ✅ LightGBM available")
    except ImportError:
        print("  ⚠️  LightGBM not available (optional)")
    
    try:
        import nltk
        print("  ✅ NLTK available")
    except ImportError:
        print("  ⚠️  NLTK not available (optional)")
    
    try:
        import cv2
        print("  ✅ OpenCV available")
    except ImportError:
        print("  ⚠️  OpenCV not available (optional)")
    
    return True


def test_ml_modules():
    """Test that ML modules can be imported and basic functionality works."""
    print("\n🔍 Testing ML modules...")
    
    try:
        from ml.model_training import SecurityModelTrainer, create_sample_security_data
        print("  ✅ Model training module imported")
        
        # Test basic functionality
        trainer = SecurityModelTrainer(model_dir="/tmp/test_models")
        sample_data = create_sample_security_data(50)
        print(f"  ✅ Created sample data: {len(sample_data)} records")
        
    except Exception as e:
        print(f"  ❌ Model training module failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ml.anomaly_detection import AnomalyDetector, create_sample_system_metrics
        print("  ✅ Anomaly detection module imported")
        
        # Test basic functionality
        detector = AnomalyDetector()
        metrics = create_sample_system_metrics()
        print(f"  ✅ Created sample metrics: {list(metrics.keys())}")
        
    except Exception as e:
        print(f"  ❌ Anomaly detection module failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ml.predictive_engine import RiskScoreEngine, create_sample_training_data
        print("  ✅ Risk scoring module imported")
        
        # Test basic functionality
        engine = RiskScoreEngine(model_dir="/tmp/test_models")
        training_data = create_sample_training_data(50)
        print(f"  ✅ Created sample training data: {len(training_data)} records")
        
    except Exception as e:
        print(f"  ❌ Risk scoring module failed: {e}")
        traceback.print_exc()
        return False
    
    return True


def test_model_training():
    """Test model training functionality."""
    print("\n🔍 Testing model training...")
    
    try:
        from ml.model_training import SecurityModelTrainer, create_sample_security_data
        
        trainer = SecurityModelTrainer(model_dir="/tmp/test_models")
        sample_data = create_sample_security_data(100)
        
        # Test anomaly detection training
        results = trainer.train_anomaly_detector(sample_data, "test_anomaly")
        print(f"  ✅ Anomaly model trained - anomaly ratio: {results['anomaly_ratio']:.3f}")
        
        # Test classification training
        results = trainer.train_classification_model(sample_data, "test_classifier")
        print(f"  ✅ Classification model trained - accuracy: {results['accuracy']:.3f}")
        
        # Test model listing
        models = trainer.list_models()
        print(f"  ✅ Models available: {models}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model training failed: {e}")
        traceback.print_exc()
        return False


def test_anomaly_detection():
    """Test anomaly detection functionality."""
    print("\n🔍 Testing anomaly detection...")
    
    try:
        from ml.anomaly_detection import AnomalyDetector, create_sample_system_metrics
        import pandas as pd
        
        detector = AnomalyDetector()
        
        # Test system metrics detection
        metrics = create_sample_system_metrics()
        alerts = detector.detect_system_metric_anomalies(metrics)
        print(f"  ✅ System metrics analyzed - {len(alerts)} alerts generated")
        
        # Test login anomaly detection with sample data
        login_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=150, freq='H'),
            'user_id': ['user1'] * 150,
            'ip_address': ['192.168.1.10'] * 150,
            'status': ['success'] * 150
        })
        
        if len(login_data) >= detector.config['min_samples_for_training']:
            login_alerts = detector.detect_login_anomalies(login_data)
            print(f"  ✅ Login patterns analyzed - {len(login_alerts)} alerts generated")
        else:
            print(f"  ⚠️  Skipped login analysis - insufficient data")
        
        # Test alert summary
        summary = detector.get_alert_summary()
        print(f"  ✅ Alert summary generated - {summary['total_alerts']} total alerts")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Anomaly detection failed: {e}")
        traceback.print_exc()
        return False


def test_risk_scoring():
    """Test risk scoring functionality."""
    print("\n🔍 Testing risk scoring...")
    
    try:
        from ml.predictive_engine import RiskScoreEngine, create_sample_training_data
        import pandas as pd
        
        engine = RiskScoreEngine(model_dir="/tmp/test_models")
        
        # Test user risk scoring
        user_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=50, freq='H'),
            'user_id': ['test_user'] * 50,
            'ip_address': ['192.168.1.10'] * 30 + ['203.0.113.1'] * 20,
            'status': ['success'] * 40 + ['failed'] * 10
        })
        
        user_risk = engine.calculate_user_risk_score('test_user', user_data)
        print(f"  ✅ User risk calculated - Score: {user_risk.risk_score:.3f}, Level: {user_risk.risk_level.value}")
        
        # Test session risk scoring
        session_data = {
            'duration_minutes': 30,
            'pages_accessed': 5,
            'failed_attempts': 0,
            'ip_address': '192.168.1.100'
        }
        
        session_risk = engine.calculate_session_risk_score('test_session', session_data)
        print(f"  ✅ Session risk calculated - Score: {session_risk.risk_score:.3f}, Level: {session_risk.risk_level.value}")
        
        # Test IP risk scoring
        ip_risk = engine.calculate_ip_risk_score('203.0.113.1', user_data)
        print(f"  ✅ IP risk calculated - Score: {ip_risk.risk_score:.3f}, Level: {ip_risk.risk_level.value}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Risk scoring failed: {e}")
        traceback.print_exc()
        return False


def test_model_persistence():
    """Test model saving and loading."""
    print("\n🔍 Testing model persistence...")
    
    try:
        from ml.model_training import SecurityModelTrainer, create_sample_security_data
        
        # Train and save a model
        trainer1 = SecurityModelTrainer(model_dir="/tmp/test_models")
        sample_data = create_sample_security_data(100)
        trainer1.train_anomaly_detector(sample_data, "persistence_test")
        
        # Load model in new trainer instance
        trainer2 = SecurityModelTrainer(model_dir="/tmp/test_models")
        loaded_model = trainer2.load_model("persistence_test")
        
        print("  ✅ Model saved and loaded successfully")
        
        # Verify model works
        features, _ = trainer2.prepare_security_data(sample_data.head(10))
        if 'persistence_test_scaler' in trainer1.scalers:
            features_scaled = trainer1.scalers['persistence_test_scaler'].transform(features)
            predictions = loaded_model.predict(features_scaled)
            print(f"  ✅ Loaded model made predictions: {len(predictions)} outputs")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model persistence failed: {e}")
        traceback.print_exc()
        return False


def run_comprehensive_test():
    """Run comprehensive ML integration test."""
    print("\n🔍 Running comprehensive integration test...")
    
    try:
        from ml.model_training import SecurityModelTrainer, create_sample_security_data
        from ml.anomaly_detection import AnomalyDetector
        from ml.predictive_engine import RiskScoreEngine, create_sample_training_data
        import pandas as pd
        
        # 1. Create components
        trainer = SecurityModelTrainer(model_dir="/tmp/test_models")
        detector = AnomalyDetector()
        engine = RiskScoreEngine(model_dir="/tmp/test_models")
        
        # 2. Generate test data
        security_logs = create_sample_security_data(200)
        training_data = create_sample_training_data(200)
        
        # 3. Train models
        trainer.train_anomaly_detector(security_logs.head(100), "integration_anomaly")
        trainer.train_classification_model(security_logs.head(100), "integration_classifier")
        
        if len(training_data) >= engine.config['min_training_samples']:
            engine.train_risk_models(training_data)
            print("  ✅ Risk models trained")
        
        # 4. Test real-time detection
        test_metrics = {'cpu_usage': 95.0, 'memory_usage': 90.0}
        alerts = detector.detect_system_metric_anomalies(test_metrics)
        
        # 5. Test risk scoring
        user_data = security_logs[security_logs['user_id'] == security_logs['user_id'].iloc[0]].head(20)
        risk_score = engine.calculate_user_risk_score('integration_test_user', user_data)
        
        print(f"  ✅ Integration test completed successfully")
        print(f"      - Models trained: {len(trainer.list_models())}")
        print(f"      - Alerts generated: {len(alerts)}")
        print(f"      - Risk score: {risk_score.risk_score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main validation function."""
    print("🤖 NoxSuite AI/ML Integration Validation")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print()
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("ML Modules", test_ml_modules),
        ("Model Training", test_model_training),
        ("Anomaly Detection", test_anomaly_detection),
        ("Risk Scoring", test_risk_scoring),
        ("Model Persistence", test_model_persistence),
        ("Comprehensive Integration", run_comprehensive_test)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! AI/ML integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())