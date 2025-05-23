import os
import sys
import pandas as pd
import sqlite3

from src.logging import logging
from src.exception import CustomException

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from joblib import dump

class Rider_Feature_Engineering_Config:
    input_data: str = os.path.join('data', 'preprocess', 'eda_report', 'riders_rfm.csv')
    rider_test_data: str = os.path.join('data', 'rider_churn_data', 'rider_test_data.csv')
    rider_train_data: str = os.path.join('data', 'rider_churn_data', 'rider_train_data.csv')
    preprocessor_pkl: str = os.path.join('data', 'rider_churn_data','preprocessor.pkl')

class Rider_Feature_Engineering:
    def __init__(self):
        self.rider_feature_engineering_config = Rider_Feature_Engineering_Config()

    def initiate_rider_feature_engineering(self):
        try:
            logging.info("Initiating Riders Feature Engineering")

            # 1) Load datasets
            conn = sqlite3.connect('ridewise.db')
            riders = pd.read_sql_query("SELECT * FROM riders", conn)
            riders_rfm = pd.read_csv(self.rider_feature_engineering_config.input_data)

            # 2) Merge datasets
            df = pd.merge(riders_rfm, riders[['user_id', 'churn_prob','age','loyalty_status','city']], on='user_id')

            # 3) Create target column
            df['churned'] = (df['churn_prob'] > 0.5).astype(int)
            df = df.drop(columns=['churn_prob'])

            target_column = 'churned'
            X = df.drop(columns=[target_column, 'user_id'])
            y = df[target_column]

            logging.info(f"Target Column Distribution: \n{y.value_counts()}")

            # 4) Build pipeline (impute median, scale with MinMaxScaler)
            categorical_columns = ['loyalty_status','city']
            numerical_columns =['recency','frequency','monetary','age']
            
            # Build a pipeline for numerical features:
            # Impute missing values using the median.
            # Scale the features using StandardScaler.  
            numerical_pipeline = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", MinMaxScaler())
            ])

            # Build a pipeline for categorical features:
            # Impute missing values using the most frequent value.
            # One-hot encode categorical features.
            categorical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("OneHotEncoder", OneHotEncoder())
            ])

            # Combine both pipelines into a single ColumnTransformer.
            preprocessor = ColumnTransformer(
                transformers=[
                    ("num_pipeline", numerical_pipeline, numerical_columns),
                    ("cat_pipeline", categorical_pipeline, categorical_columns)
            ])

            # 5) Fit and transform X with numerical pipeline
            X_transformed = preprocessor.fit_transform(X)
            # Save preprocessor object after fitting
            dump(preprocessor, self.rider_feature_engineering_config.preprocessor_pkl)
            logging.info("Preprocessor saved to models/preprocessor.pkl")

            ## Retrieve column names generated by the OneHotEncoder for categorical features.
            ohe = preprocessor.named_transformers_["cat_pipeline"].named_steps["OneHotEncoder"]
            ohe_feature_names = list(ohe.get_feature_names_out(categorical_columns))

            # Combine numeric columns with one-hot encoded categorical column names.
            final_columns = numerical_columns + ohe_feature_names

            # Construct a new DataFrame with the transformed features.
            X_transformed_df = pd.DataFrame(X_transformed, columns=final_columns)

            # 7) Apply SMOTE for balancing classes
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X_transformed_df, y)

            logging.info(f"After SMOTE - Class 1: {sum(y_resampled == 1)}, Class 0: {sum(y_resampled == 0)}")

            # 8) Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled
            )

            # 9) Save train/test DataFrames
            train_df = pd.concat([X_train, pd.Series(y_train, name=target_column)], axis=1)
            test_df = pd.concat([X_test, pd.Series(y_test, name=target_column)], axis=1)

            train_df.to_csv(self.rider_feature_engineering_config.rider_train_data, index=False)
            test_df.to_csv(self.rider_feature_engineering_config.rider_test_data, index=False)

            logging.info("Train and test datasets saved successfully")
            logging.info(f"Train_df shape: {train_df.shape}")
            logging.info(f"Test_df shape: {test_df.shape}")

        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    rider_feature_engineering = Rider_Feature_Engineering()
    rider_feature_engineering.initiate_rider_feature_engineering()
