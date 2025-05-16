import sqlite3
import pandas as pd
import os
import sys
from dataclasses import dataclass
from ydata_profiling import ProfileReport
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from datetime import datetime

from src.exception import CustomException
from src.logging import logging

class Data_Preprocessing_Config:
    preprocessed_data: str = os.path.join('data', 'preprocess', 'eda_report')
    out_dir: str = os.path.join('data', 'preprocess', 'eda_report')
    map_dir: str = os.path.join('data', 'preprocess', 'maps')

class Data_Preprocessing:
    def __init__(self):
        self.data_preprocessing_config = Data_Preprocessing_Config()

    def initiating_data_preprocessing(self):
        logging.info("Data Preprocessing Initiated")
        try:
            conn = sqlite3.connect('ridewise.db')

            # Step 1: Read data from DB
            riders = pd.read_sql_query("SELECT * FROM riders", conn)
            trip = pd.read_sql_query("SELECT * FROM trips", conn)
            drivers = pd.read_sql_query("SELECT * FROM drivers", conn)
            session = pd.read_sql_query("SELECT * FROM sessions", conn)
            promotions = pd.read_sql_query("SELECT * FROM promotions", conn)

            # Step 2: Create folders
            os.makedirs(self.data_preprocessing_config.out_dir, exist_ok=True)
            os.makedirs(self.data_preprocessing_config.map_dir, exist_ok=True)

            # Step 3: Save profiling reports
            dataframes = {
                "riders": riders,
                "trips": trip,
                "drivers": drivers,
                "sessions": session,
                "promotions": promotions
            }

            for name, df in dataframes.items():
                report = ProfileReport(df, title=f"{name.capitalize()} Data Report", explorative=True)
                output_path = os.path.join(self.data_preprocessing_config.out_dir, f"{name}_eda_report.html")
                report.to_file(output_path)
                logging.info(f"Saved EDA report for {name} to {output_path}")

            # Step 4: Convert datetime columns
            trip['pickup_time'] = pd.to_datetime(trip['pickup_time'], utc=True)
            trip['dropoff_time'] = pd.to_datetime(trip['dropoff_time'], utc=True)
            session['session_time'] = pd.to_datetime(session['session_time'], utc=True)
            drivers['signup_date'] = pd.to_datetime(drivers['signup_date'], utc=True)
            drivers['last_active'] = pd.to_datetime(drivers['last_active'], utc=True)
            riders['signup_date'] = pd.to_datetime(riders['signup_date'], utc=True)
            logging.info("Datetime conversion complete")

            # Step 5: Top 50 Popular Routes
            route_counts = trip.groupby(['pickup_lat', 'pickup_lng', 'dropoff_lat', 'dropoff_lng']).size().reset_index(name='route_count')
            popular_routes = route_counts.sort_values(by='route_count', ascending=False).head(50)
            popular_routes.to_csv(os.path.join(self.data_preprocessing_config.out_dir, "top_50_popular_routes.csv"), index=False)
            logging.info("Top 15 popular routes:\n" + popular_routes.to_string(index=False))

            # Step 6: Peak Times by Hour
            trip['pickup_hour'] = trip['pickup_time'].dt.hour
            peak_times = trip.groupby('pickup_hour').size().reset_index(name='trip_count')
            peak_times.to_csv(os.path.join(self.data_preprocessing_config.out_dir, "peak_times_by_hour.csv"), index=False)
            
            plt.figure(figsize=(10, 6))
            sns.barplot(x='pickup_hour', y='trip_count', data=peak_times)
            plt.title('Number of Trips by Hour of the Day (Peak Times)')
            plt.xlabel('Hour of the Day')
            plt.ylabel('Number of Trips')
            plt.tight_layout()
            plt.savefig(os.path.join(self.data_preprocessing_config.out_dir, "peak_times.png"))
            plt.close()
            logging.info("Saved peak times bar chart")

            # Step 7: Rider RFM
            rider_frequency = trip.groupby('user_id').size().reset_index(name='frequency')
            recency = (pd.to_datetime('today', utc=True) - trip.groupby('user_id')['pickup_time'].max()).dt.days
            monetary = trip.groupby('user_id')['fare'].sum()

            rfm = pd.DataFrame({
            'user_id': recency.index,
            'recency': recency.values,
            'frequency': rider_frequency['frequency'],
            'monetary': monetary.values
            })
            rfm.to_csv(os.path.join(self.data_preprocessing_config.out_dir, "riders_rfm.csv"), index=False)
            logging.info("Calculated RFM metrics for riders")

            # Step 8: Driver Activity
            driver_activity = drivers[['driver_id', 'rating', 'acceptance_rate', 'last_active']].copy()
            driver_activity['days_since_last_active'] = (pd.to_datetime('today', utc=True) - driver_activity['last_active']).dt.days
            driver_activity.to_csv(os.path.join(self.data_preprocessing_config.out_dir, "driver_activity.csv"), index=False)
            logging.info("Driver Activity Sample:\n" + driver_activity.head(10).to_string(index=False))

            # Step 9: Referral Chains
            referral_chain = riders.groupby('referred_by').size().reset_index(name='referral_count')
            referral_chain.to_csv(os.path.join(self.data_preprocessing_config.out_dir, "referral_chains.csv"), index=False)
            logging.info("Top 10 Referral Chains:\n" + referral_chain.sort_values('referral_count', ascending=False).head(10).to_string(index=False))

            # Step 10: Geospatial Maps (Folium)
            # Pickup locations
            pickup_map = folium.Map(location=[trip['pickup_lat'].mean(), trip['pickup_lng'].mean()], zoom_start=12)
            pickup_cluster = MarkerCluster().add_to(pickup_map)
            for _, row in trip.sample(500, random_state=42).iterrows():
                folium.Marker(location=[row['pickup_lat'], row['pickup_lng']], popup="Pickup").add_to(pickup_cluster)
            pickup_map.save(os.path.join(self.data_preprocessing_config.map_dir, "pickup_locations_map.html"))

            # Dropoff locations
            dropoff_map = folium.Map(location=[trip['dropoff_lat'].mean(), trip['dropoff_lng'].mean()], zoom_start=12)
            dropoff_cluster = MarkerCluster().add_to(dropoff_map)
            for _, row in trip.sample(500, random_state=42).iterrows():
                folium.Marker(location=[row['dropoff_lat'], row['dropoff_lng']], popup="Dropoff").add_to(dropoff_cluster)
            dropoff_map.save(os.path.join(self.data_preprocessing_config.map_dir, "dropoff_locations_map.html"))
            logging.info("Saved geospatial pickup and dropoff maps")

        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    eda = Data_Preprocessing()
    eda.initiating_data_preprocessing()