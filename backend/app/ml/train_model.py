"""
Trains the attrition-risk classifier from employee data currently in the
database (both active and exited employees, so the model learns real
outcome labels rather than a synthetic proxy). Intended to be re-run
periodically (e.g. monthly, via a scheduled job) as more outcomes accrue.

Usage:
    python -m app.ml.train_model
"""
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
)

from app import create_app
from app.extensions import db
from app.models.employee import Employee
from app.config import Config

FEATURE_COLUMNS = [
    "tenure_years",
    "monthly_salary",
    "last_salary_hike_pct",
    "promotions_count",
    "years_since_last_promotion",
    "performance_score",
    "satisfaction_score",
    "attendance_pct",
    "overtime_hours_monthly",
    "leave_days_taken_ytd",
    "training_hours_ytd",
    "distance_from_home_km",
    "remote_ratio_pct",
]


def load_training_frame() -> pd.DataFrame:
    employees = Employee.query.all()
    rows = []
    for e in employees:
        row = e.ml_feature_dict()
        row["attrited"] = int(e.attrited)
        rows.append(row)
    return pd.DataFrame(rows)


def train_and_save(app=None):
    app = app or create_app()
    with app.app_context():
        df = load_training_frame()
        if df.empty or df["attrited"].nunique() < 2:
            raise RuntimeError(
                "Not enough labeled data to train (need both attrited and retained "
                "employees). Run the seed script first: python -m app.seed"
            )

        X = df[FEATURE_COLUMNS]
        y = df["attrited"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
            "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
            "train_size": len(X_train),
            "test_size": len(X_test),
            "feature_importance": {
                col: round(float(imp), 4)
                for col, imp in sorted(
                    zip(FEATURE_COLUMNS, model.feature_importances_),
                    key=lambda x: x[1], reverse=True,
                )
            },
        }

        os.makedirs(Config.ML_MODEL_DIR, exist_ok=True)
        joblib.dump({"model": model, "features": FEATURE_COLUMNS}, Config.ML_MODEL_PATH)
        with open(Config.ML_METRICS_PATH, "w") as f:
            json.dump(metrics, f, indent=2)

        print("Model trained and saved to", Config.ML_MODEL_PATH)
        print(json.dumps(metrics, indent=2))
        return metrics


if __name__ == "__main__":
    train_and_save()
