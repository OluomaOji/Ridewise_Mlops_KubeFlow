import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from joblib import dump
import shap

from src.logging import logging
from src.exception import CustomException


class Rider_Churn_config:
    rider_test_data: str = os.path.join('data', 'rider_churn_data', 'rider_test_data.csv')
    rider_train_data: str = os.path.join('data', 'rider_churn_data', 'rider_train_data.csv')
    MLFLOW_TRACKING_URI: str= "https://gbemimaks:e376547141e9bed159a40749d6af1480f0ed58a7@dagshub.com/gbemimaks/Ridewise_Mlops_KubeFlow.mlflow"
    MLFLOW_TRACKING_USERNAME: str = "gbemimaks"
    MLFLOW_TRACKING_PASSWORD: str = "760c90844a305272f1981be1879bceef551c3385"
    MLFLOW_TRCKING_TOKEN: str = "e376547141e9bed159a40749d6af1480f0ed58a7"
    best_model_path: str = os.path.join('data', 'rider_churn_data', 'best_model.pkl')
    shap_summary: str = os.path.join('data','rider_churn_data','shap_summary.png')

class Rider_Churn_ModelTraining:
    def __init__(self):
        self.rider_churn_config = Rider_Churn_config()

    def initiate_rider_churn(self):
        try:
            # Load the Train and Test Datasets
            train_data = pd.read_csv(self.rider_churn_config.rider_train_data)
            test_data = pd.read_csv(self.rider_churn_config.rider_test_data)

            target_column = 'churned'
            X_train = train_data.drop(columns=target_column).astype(float)
            y_train = train_data[target_column]
            X_test = test_data.drop(columns=target_column).astype(float)
            y_test = test_data[target_column]

            # Define models
            models = {
                "Random Forest Classifier": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=1),
                "Gradient Boosting Classifier": GradientBoostingClassifier(n_estimators=100),
                "SVM Classifier": SVC(probability=True),
                "Logistic Regression": LogisticRegression(max_iter=1000,random_state=42)
            }

            best_model = None
            best_model_name = None
            best_score = float("-inf")

            # Set MLflow environment variables
            os.environ["MLFLOW_TRACKING_URI"] = self.rider_churn_config.MLFLOW_TRACKING_URI
            os.environ["MLFLOW_TRACKING_USERNAME"] = self.rider_churn_config.MLFLOW_TRACKING_USERNAME
            os.environ["MLFLOW_TRACKING_PASSWORD"] = self.rider_churn_config.MLFLOW_TRACKING_PASSWORD
            mlflow.set_tracking_uri(self.rider_churn_config.MLFLOW_TRACKING_URI)
            mlflow.set_experiment("Rider_Churn_Prediction")

            # Train and log each model
            for model_name, model in models.items():
                with mlflow.start_run(run_name=model_name):
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

                    acc = accuracy_score(y_test, y_pred)
                    precision = precision_score(y_test, y_pred)
                    recall = recall_score(y_test, y_pred)
                    f1 = f1_score(y_test, y_pred)
                    roc_auc = roc_auc_score(y_test, y_proba)

                    mlflow.log_params({"model": model_name})
                    mlflow.log_metrics({
                        "accuracy": acc,
                        "precision": precision,
                        "recall": recall,
                        "f1_score": f1,
                        "roc_auc": roc_auc
                    })

                    signature = infer_signature(X_train, model.predict(X_train))
                    mlflow.sklearn.log_model(model, "model", signature=signature, input_example=X_train.head(1))

                    if roc_auc > best_score:
                        best_score = roc_auc
                        best_model = model
                        best_model_name = model_name

            # Save the best model
            if best_model:
                dump(best_model, self.rider_churn_config.best_model_path)
                print(f"Best model '{best_model_name}' saved to {self.rider_churn_config.best_model_path}")
                # SHAP explainability
                self.generate_shap_summary(best_model, X_test)
            else:
                print("No best model was selected.")

        except Exception as e:
            raise CustomException(e, sys)

    def generate_shap_summary(self, model, X_test):
        try:
            explainer = shap.Explainer(model, X_test)
            # Generate SHAP values
            shap_values = explainer(X_test, check_additivity=False)

            # Plot and save summary
            plt.figure()
            shap.summary_plot(shap_values, X_test, show=False)
            os.makedirs(os.path.dirname(self.rider_churn_config.shap_summary), exist_ok=True)
            plt.savefig(self.rider_churn_config.shap_summary, bbox_inches='tight')
            plt.close()

            mlflow.log_artifact(self.rider_churn_config.shap_summary)

            logging.info(f"SHAP summary plot saved to {self.rider_churn_config.shap_summary}")
        
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    trainer = Rider_Churn_ModelTraining()
    trainer.initiate_rider_churn()
