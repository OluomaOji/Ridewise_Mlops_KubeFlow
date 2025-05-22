import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

import shap
import joblib

from src.logging import logging
from src.exception import CustomException


class Rider_Churn_Shap_Config:
    rider_test_data: str = os.path.join('data', 'rider_churn_data', 'rider_test_data.csv')
    rider_train_data: str = os.path.join('data', 'rider_churn_data', 'rider_train_data.csv')
    best_model_path: str = os.path.join('data', 'rider_churn_data', 'best_model.pkl')
    shap_summary: str = os.path.join('data', 'rider_churn_data', 'shap_summary.png')


class Rider_Churn_Shap:
    def __init__(self):
        self.config = Rider_Churn_Shap_Config()

    def generate_shap_summary(self):
        try:
            # Load the Train and Test Datasets
            train_data = pd.read_csv(self.config.rider_train_data)
            test_data = pd.read_csv(self.config.rider_test_data)

            target_column = 'churned'
            X_train = train_data.drop(columns=[target_column]).astype(float)
            y_train = train_data[target_column]
            X_test = test_data.drop(columns=[target_column]).astype(float)
            y_test = test_data[target_column]

            # Load the trained model
            model = joblib.load(self.config.best_model_path)

            # Use SHAP TreeExplainer or KernelExplainer depending on model type
            explainer = shap.Explainer(model, X_train)
            shap_values = explainer(X_test)

            # Plot SHAP summary
            plt.figure()
            shap.summary_plot(shap_values, X_test, show=False)

            # Save SHAP plot
            os.makedirs(os.path.dirname(self.config.shap_summary), exist_ok=True)
            plt.savefig(self.config.shap_summary, bbox_inches='tight')

            print(f"SHAP summary plot saved to {self.config.shap_summary}")
        except Exception as e:
            raise CustomException(sys, e)
if __name__ == "__main__":
    shap_generation = Rider_Churn_Shap()
    shap_generation.generate_shap_summary()