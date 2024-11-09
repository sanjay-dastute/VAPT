import sys
print(f"Python version: {sys.version}")

import fastapi
print(f"FastAPI version: {fastapi.__version__}")

import sqlalchemy
print(f"SQLAlchemy version: {sqlalchemy.__version__}")

import tensorflow as tf
print(f"TensorFlow version: {tf.__version__}")

print("\nAll critical components verified successfully!")
