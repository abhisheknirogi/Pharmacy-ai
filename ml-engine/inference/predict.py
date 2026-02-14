"""
Inference module for ML predictions.
Loads trained models or falls back to baseline heuristics.
"""
import pickle
import os
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReorderPredictor:
    """ML-based reorder quantity predictor."""

    def __init__(self, model_path=None):
        self.model_path = model_path or "ml-engine/models"
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load trained model or initialize baseline."""
        model_file = os.path.join(self.model_path, "reorder_model.pkl")

        if os.path.exists(model_file):
            try:
                with open(model_file, "rb") as f:
                    self.model = pickle.load(f)
                logger.info(f"✅ Loaded ML model from {model_file}")
            except Exception as e:
                logger.warning(f"Could not load model: {e}. Using baseline heuristic.")
                self.model = None
        else:
            logger.info("No ML model found. Using baseline heuristic.")
            self.model = None

    def predict(self, sales_history: list, current_stock: int, days_ahead: int = 7):
        """
        Predict reorder quantity.

        Args:
            sales_history: List of daily sales quantities (last 90 days)
            current_stock: Current inventory quantity
            days_ahead: Days to forecast for

        Returns:
            dict with prediction details
        """
        if self.model:
            return self._ml_predict(sales_history, current_stock, days_ahead)
        else:
            return self._baseline_predict(sales_history, current_stock, days_ahead)

    def _ml_predict(self, sales_history: list, current_stock: int, days_ahead: int):
        """ML-based prediction (placeholder for future models)."""
        # For now, use baseline - implement actual ML later
        return self._baseline_predict(sales_history, current_stock, days_ahead)

    def _baseline_predict(self, sales_history: list, current_stock: int, days_ahead: int):
        """Baseline heuristic prediction using moving average."""
        if not sales_history or len(sales_history) == 0:
            # No history - use conservative estimate
            return {
                "suggested_quantity": 0,
                "confidence": 0.1,
                "method": "baseline_no_history",
                "reason": "Insufficient data - recommend manual review"
            }

        # Convert to numpy array for calculations
        history_array = np.array(sales_history)

        # Calculate moving average (7-day window if available)
        window = min(7, len(history_array))
        avg_daily_sales = np.mean(history_array[-window:])

        # Forecast demand
        forecasted_demand = avg_daily_sales * days_ahead

        # Calculate safety stock (2 weeks of average sales)
        safety_stock = avg_daily_sales * 14

        # Required quantity
        required_qty = forecasted_demand + safety_stock - current_stock
        suggested_qty = max(0, int(np.ceil(required_qty)))

        # Confidence based on data quality
        if len(history_array) >= 30:
            confidence = 0.85
        elif len(history_array) >= 14:
            confidence = 0.60
        else:
            confidence = 0.40

        return {
            "suggested_quantity": suggested_qty,
            "confidence": confidence,
            "method": "baseline_ma7",
            "average_daily_sales": round(avg_daily_sales, 2),
            "forecasted_demand": round(forecasted_demand, 2),
            "safety_stock": round(safety_stock, 2),
            "days_of_current_stock": round(current_stock / avg_daily_sales, 1) if avg_daily_sales > 0 else 999
        }


def get_predictor():
    """Get predictor instance."""
    return ReorderPredictor()
