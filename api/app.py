from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd

#Load Model and Preprocessing Object
model = joblib.load("data/rider_churn_data/best_model.pkl")
preprocessor = joblib.load("data/rider_churn_data/preprocessor.pkl")

app = FastAPI(
    title="Rider Churn Prediction API",
    description="API to predict rider churn using metadata",
    version="1.0.0"
)

class UserMetadata(BaseModel):
    recency: float
    frequency: float
    monetary: float
    age: int
    loyalty_status: str
    city: str

@app.post("/predict")
def predict_churn(user: UserMetadata):
    try:
        input_df = pd.DataFrame([user.dict()])
        transformed_input = preprocessor.transform(input_df)
        prediction = model.predict(transformed_input)
        prediction_proba = model.predict_proba(transformed_input)[0][1]

        return {
            "churn_prediction": int(prediction[0]),
            "churn_probability": round(prediction_proba, 3)
        }
    except Exception as e:
        return {"error": str(e)}