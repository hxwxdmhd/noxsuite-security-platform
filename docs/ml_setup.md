# NoxSuite AI/ML Setup Guide

This document provides step-by-step instructions for setting up and using the AI/ML capabilities in the NoxSuite Security Platform.

## 📋 Prerequisites

### System Requirements
- Python 3.12+ 
- 8GB+ RAM (16GB recommended for training)
- 2GB+ available disk space
- Optional: NVIDIA GPU for accelerated training

### Required Knowledge
- Basic Python programming
- Understanding of machine learning concepts
- Familiarity with security log analysis

## 🚀 Installation

### Option 1: pip (Quick Setup)

```bash
# Clone the repository
git clone https://github.com/hxwxdmhd/noxsuite-security-platform.git
cd noxsuite-security-platform

# Install all dependencies including AI/ML libraries
pip install -r requirements.txt

# Verify installation
python -c "import ml; print('✅ ML modules available')"
```

### Option 2: Conda (Recommended)

```bash
# Clone the repository
git clone https://github.com/hxwxdmhd/noxsuite-security-platform.git
cd noxsuite-security-platform

# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate noxsuite-security-platform

# Verify installation
python -c "import ml; print('✅ ML modules available')"
```

### Option 3: Docker (Isolated Environment)

```bash
# Build Docker image with ML dependencies
docker build -f Dockerfile.ai -t noxsuite-ml .

# Run container with ML capabilities
docker run -it --rm -v $(pwd):/workspace noxsuite-ml bash
```

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# AI/ML Configuration
ML_MODEL_DIR=./models
ML_ENABLE_GPU=false
ML_LOG_LEVEL=INFO
ML_RANDOM_SEED=42

# Training Configuration  
ML_BATCH_SIZE=32
ML_EPOCHS=100
ML_LEARNING_RATE=0.001

# Anomaly Detection Settings
ANOMALY_CONTAMINATION_RATE=0.1
ANOMALY_ALERT_THRESHOLD=0.8

# Risk Scoring Settings
RISK_MODEL_RETRAIN_INTERVAL=7d
RISK_CONFIDENCE_THRESHOLD=0.7
```

### GPU Support (Optional)

For NVIDIA GPU acceleration:

```bash
# Install CUDA-enabled libraries
pip install tensorflow-gpu torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Enable GPU in environment
export ML_ENABLE_GPU=true
export CUDA_VISIBLE_DEVICES=0
```

## 📊 Quick Start

### 1. Basic Model Training

```python
from ml.model_training import SecurityModelTrainer, create_sample_security_data

# Initialize trainer
trainer = SecurityModelTrainer(model_dir="./models")

# Create sample data (replace with your security logs)
security_logs = create_sample_security_data(1000)

# Train anomaly detection model
results = trainer.train_anomaly_detector(security_logs)
print(f"Model trained with {results['anomaly_ratio']:.2%} anomaly rate")

# Train threat classification model
results = trainer.train_classification_model(security_logs)
print(f"Classification accuracy: {results['accuracy']:.2%}")
```

### 2. Real-time Anomaly Detection

```python
from ml.anomaly_detection import AnomalyDetector, create_sample_system_metrics

# Initialize detector
detector = AnomalyDetector()

# Monitor system metrics
for i in range(10):
    metrics = create_sample_system_metrics()
    alerts = detector.detect_system_metric_anomalies(metrics)
    
    if alerts:
        for alert in alerts:
            print(f"🚨 {alert.severity.upper()}: {alert.description}")

# Get summary
summary = detector.get_alert_summary()
print(f"Total alerts: {summary['total_alerts']}")
```

### 3. Risk Scoring

```python
from ml.predictive_engine import RiskScoreEngine, create_sample_training_data
import pandas as pd

# Initialize risk engine
engine = RiskScoreEngine(model_dir="./models")

# Train risk models (optional - uses rule-based scoring by default)
training_data = create_sample_training_data(500)
training_results = engine.train_risk_models(training_data)

# Create user activity data
user_data = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
    'user_id': ['user123'] * 100,
    'ip_address': ['192.168.1.10'] * 80 + ['203.0.113.1'] * 20,
    'status': ['success'] * 90 + ['failed'] * 10
})

# Calculate user risk score
risk_score = engine.calculate_user_risk_score('user123', user_data)
print(f"User Risk: {risk_score.risk_score:.3f} ({risk_score.risk_level.value})")
print(f"Recommendations: {', '.join(risk_score.recommendations)}")
```

## 📝 Data Preparation

### Security Log Format

Your security logs should include these columns:

```python
required_columns = [
    'timestamp',    # datetime - when the event occurred
    'user_id',      # string - identifier for the user
    'ip_address',   # string - source IP address
    'status',       # string - 'success', 'failed', 'blocked'
    'action',       # string - type of action performed
    'resource'      # string - resource accessed (optional)
]
```

### Example Log Data

```python
import pandas as pd

security_logs = pd.DataFrame({
    'timestamp': ['2024-01-01 09:00:00', '2024-01-01 09:01:00'],
    'user_id': ['john.doe', 'jane.smith'],
    'ip_address': ['192.168.1.100', '203.0.113.50'],
    'status': ['success', 'failed'],
    'action': ['login', 'login'],
    'resource': ['/dashboard', '/admin']
})
```

## 🧪 Running Tests

### Unit Tests

```bash
# Run all ML tests
pytest tests/ml/ -v

# Run specific test modules
pytest tests/ml/test_model_training.py -v
pytest tests/ml/test_anomaly_detection.py -v
pytest tests/ml/test_predictive_engine.py -v

# Run with coverage
pytest tests/ml/ --cov=ml --cov-report=html
```

### Integration Tests

```bash
# Test complete ML workflow
python -m ml.model_training
python -m ml.anomaly_detection
python -m ml.predictive_engine
```

### Notebook Tests

```bash
# Install Jupyter if not already installed
pip install jupyter

# Run demo notebooks
jupyter notebook notebooks/ai_ml_integration_demo.ipynb
jupyter notebook notebooks/security_log_nlp_analysis.ipynb
```

## 🔍 Model Management

### Saving and Loading Models

```python
from ml.model_training import SecurityModelTrainer

# Initialize trainer
trainer = SecurityModelTrainer(model_dir="./models")

# Train and save model
trainer.train_anomaly_detector(data, "my_anomaly_model")

# List available models
models = trainer.list_models()
print(f"Available models: {models}")

# Load existing model
loaded_model = trainer.load_model("my_anomaly_model")
```

### Model Versioning

```python
from datetime import datetime

# Include timestamp in model names
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
model_name = f"anomaly_detector_{timestamp}"

trainer.train_anomaly_detector(data, model_name)
```

## 📈 Performance Tuning

### Memory Optimization

```python
# For large datasets, use chunking
def process_large_dataset(data, chunk_size=1000):
    for chunk in pd.read_csv(data, chunksize=chunk_size):
        # Process chunk
        yield process_chunk(chunk)

# Enable memory mapping for large models
import joblib
joblib.dump(model, 'model.pkl', compress=3)
```

### GPU Acceleration

```python
# Check GPU availability
import torch
if torch.cuda.is_available():
    print(f"GPU available: {torch.cuda.get_device_name()}")
    device = torch.device('cuda')
else:
    print("Using CPU")
    device = torch.device('cpu')

# Use GPU for TensorFlow
import tensorflow as tf
if tf.config.list_physical_devices('GPU'):
    print("GPU available for TensorFlow")
```

### Parallel Processing

```python
# Use multiple cores for scikit-learn
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_jobs=-1)  # Use all available cores

# Parallel feature extraction
from joblib import Parallel, delayed

def parallel_feature_extraction(data_chunks):
    return Parallel(n_jobs=-1)(
        delayed(extract_features)(chunk) for chunk in data_chunks
    )
```

## 🚨 Troubleshooting

### Common Issues

#### ImportError: No module named 'ml'

```bash
# Ensure you're in the correct directory
cd /path/to/noxsuite-security-platform

# Check Python path
python -c "import sys; print(sys.path)"

# Add current directory to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Memory Errors During Training

```python
# Reduce batch size
trainer.config['batch_size'] = 16

# Use chunked processing
def train_in_chunks(data, chunk_size=500):
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        trainer.train_anomaly_detector(chunk, f"model_chunk_{i}")
```

#### GPU Out of Memory

```python
# Reduce model complexity
model = RandomForestClassifier(n_estimators=50)  # Instead of 100

# Clear GPU cache (PyTorch)
import torch
torch.cuda.empty_cache()

# Enable memory growth (TensorFlow)
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

### Performance Issues

```bash
# Profile ML code
python -m cProfile -s cumulative ml/model_training.py

# Monitor memory usage
pip install memory_profiler
python -m memory_profiler ml/anomaly_detection.py

# Use faster libraries
pip install intel-scikit-learn  # Intel-optimized scikit-learn
```

## 🔧 Advanced Configuration

### Custom Anomaly Detection Rules

```python
from ml.anomaly_detection import AnomalyDetector

# Custom configuration
config = {
    'contamination_rate': 0.05,  # Expect 5% anomalies
    'alert_threshold': 0.9,      # High threshold
    'severity_thresholds': {
        'critical': 0.95,
        'high': 0.8,
        'medium': 0.6,
        'low': 0.4
    }
}

detector = AnomalyDetector(config_path='custom_config.json')
```

### Custom Risk Scoring Models

```python
from ml.predictive_engine import RiskScoreEngine

class CustomRiskEngine(RiskScoreEngine):
    def _calculate_rule_based_risk_score(self, features, entity_type):
        # Custom risk calculation logic
        risk = super()._calculate_rule_based_risk_score(features, entity_type)
        
        # Add custom factors
        if entity_type == 'user':
            # Increase risk for admin users
            if 'admin' in features.get('role', ''):
                risk *= 1.2
                
        return min(risk, 1.0)

# Use custom engine
custom_engine = CustomRiskEngine()
```

### Model Ensemble Configuration

```python
# Configure model ensemble weights
ensemble_config = {
    'models': {
        'xgboost': {'weight': 0.4, 'enabled': True},
        'lightgbm': {'weight': 0.3, 'enabled': True},
        'random_forest': {'weight': 0.3, 'enabled': True}
    },
    'voting': 'soft',  # Use probability averaging
    'fallback': 'rule_based'  # Fallback if models fail
}
```

## 📚 Additional Resources

### Documentation
- [TensorFlow Documentation](https://www.tensorflow.org/guide)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [NLTK Documentation](https://www.nltk.org/)

### Tutorials
- [Security Data Science](https://www.packtpub.com/product/hands-on-machine-learning-for-cybersecurity/9781788992282)
- [Anomaly Detection in Practice](https://blog.ml.cmu.edu/2020/08/31/3-anomaly-detection/)

### Sample Datasets
- [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html)
- [KDD Cup 1999](http://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html)
- [NSL-KDD](https://www.unb.ca/cic/datasets/nsl.html)

## 🆘 Support

### Getting Help

1. **Check the logs**: Enable debug logging with `ML_LOG_LEVEL=DEBUG`
2. **Review test cases**: Look at `tests/ml/` for usage examples
3. **Run diagnostics**: Use `python -m ml.model_training --test`
4. **Check dependencies**: Run `pip list | grep -E "tensor|torch|sklearn"`

### Reporting Issues

When reporting ML-related issues, include:
- Python version and platform
- Full error traceback
- Data sample (anonymized)
- Environment configuration
- Steps to reproduce

### Performance Monitoring

```python
import time
import psutil

def monitor_training(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        print(f"Training time: {end_time - start_time:.2f}s")
        print(f"Memory used: {(end_memory - start_memory) / 1024**2:.2f}MB")
        
        return result
    return wrapper

@monitor_training
def train_model():
    # Your training code here
    pass
```

---

**✅ You're now ready to use the AI/ML capabilities in NoxSuite!**

For additional support, consult the inline documentation in the ML modules or run the interactive notebooks for hands-on examples.