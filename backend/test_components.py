import sys
print(f"Python version: {sys.version}")

import tensorflow as tf
print(f"TensorFlow version: {tf.__version__}")

from fastapi import FastAPI
print("FastAPI imported successfully")

from sqlalchemy import create_engine
print("SQLAlchemy imported successfully")

from app.core.ai.vulnerability_detector import VulnerabilityDetector
print("VulnerabilityDetector imported successfully")

from app.core.scanners.web_scanner import WebScanner
print("WebScanner imported successfully")

print("\nAll critical components verified successfully!")
