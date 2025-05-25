 feature select 
features = df[[  'pickup_time', 'pickup_lat', 'pickup_lng', 'dropoff_time', 'dropoff_lng', 'city', 'weather', 'surge_multiplier']]


# convert pickup_time and dropoff_time to datetime
features['pickup_time'] = pd.to_datetime(features['pickup_time'])
features['dropoff_time'] = pd.to_datetime(features['dropoff_time'])

features['pickup_hour'] = features['pickup_time'].dt.hour
features['pickup_day'] = features['pickup_time'].dt.dayofweek
features['trip_duration_minutes'] = (features['dropoff_time'] - features['pickup_time']).dt.total_seconds() / 60


X = features[['pickup_hour', 'pickup_day', 'trip_duration_minutes', 'pickup_lat', 'pickup_lng', 'dropoff_lng', 'city', 'weather']]
y= features['surge_multiplier']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# define the preprocessing steps
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['pickup_hour', 'pickup_day', 'trip_duration_minutes', 'pickup_lat', 'pickup_lng', 'dropoff_lng']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
    ])


# create the pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', model)
    
])
# define the model
model = CatBoostRegressor(
    iterations=2000,
    learning_rate=0.2,
    depth=8,
    l2_leaf_reg=3,
    random_strength=1,
    loss_function='RMSE',
    early_stopping_rounds=100,
    verbose=200
)
pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
y_pred