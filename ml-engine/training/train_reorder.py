"""
Training script for reorder prediction model.
Uses historical sales data to train a simple regression model.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import pickle
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_features_from_sales(sales_df: pd.DataFrame, lookback_days: int = 7):
    """
    Create time-series features from sales data.
    Features: moving average, trend, day of week, etc.
    """
    features = []
    targets = []

    for i in range(lookback_days, len(sales_df) - 1):
        window = sales_df.iloc[i - lookback_days:i]
        ma = window['quantity'].mean()
        trend = window['quantity'].iloc[-1] - window['quantity'].iloc[0]
        std = window['quantity'].std()

        # Current features
        X = [ma, trend, std]
        # Target: next day sales
        y = sales_df.iloc[i + 1]['quantity']

        features.append(X)
        targets.append(y)

    return np.array(features), np.array(targets)


def train_reorder_model(data_path: str = "ml-engine/data/processed/sales_data.csv"):
    """
    Train the reorder prediction model.
    Requires training data in CSV format.
    """
    model_dir = "ml-engine/models"
    os.makedirs(model_dir, exist_ok=True)

    try:
        # Load training data
        if not os.path.exists(data_path):
            logger.warning(f"Training data not found at {data_path}")
            logger.info("Create a CSV file with columns: date, medicine_name, quantity")
            return None

        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} records from {data_path}")

        # Prepare data
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Create features
        X, y = create_features_from_sales(df, lookback_days=7)

        if len(X) < 10:
            logger.warning("Insufficient training data (need >10 samples)")
            return None

        # Train model
        model = LinearRegression()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model.fit(X_scaled, y)

        # Save model
        model_path = os.path.join(model_dir, "reorder_model.pkl")
        scaler_path = os.path.join(model_dir, "scaler.pkl")

        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)

        # Metrics
        train_score = model.score(X_scaled, y)
        logger.info(f"✅ Model trained with R² score: {train_score:.4f}")
        logger.info(f"💾 Model saved to {model_path}")

        return model

    except Exception as e:
        logger.error(f"Error training model: {e}")
        return None


def train_expiry_model(data_path: str = "ml-engine/data/processed/medicine_data.csv"):
    """
    Train expiry detection model.
    For now, this is a placeholder for future ML models.
    """
    logger.info("Expiry model training not yet implemented")
    logger.info("Current system uses rule-based expiry detection")


if __name__ == "__main__":
    logger.info("Starting model training...")
    model = train_reorder_model()
    if model:
        logger.info("✅ Training completed successfully")
    else:
        logger.info("⚠️ Training skipped or failed - using baseline predictions")
