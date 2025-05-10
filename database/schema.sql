-- TABLE 1 - RIDERS TABLE
CREATE TABLE riders (
    user_id VARCHAR(64) PRIMARY KEY,
    signup_date DATE,
    loyalty_status TEXT,
    age INTEGER,
    city TEXT,
    avg_rating_given FLOAT,
    churn_prob FLOAT,
    referred_by TEXT
);

-- TABLE 2 - DRIVERS TABLE
CREATE TABLE drivers (
    driver_id VARCHAR(64) PRIMARY KEY,
    rating FLOAT,
    vehicle_type TEXT,
    signup_date DATE,
    last_active DATE,
    city TEXT,
    acceptance_rate FLOAT
); 

-- TABLE 3 - TRIPS TABLE
CREATE TABLE trips (
    trip_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES riders(user_id),
    driver_id VARCHAR(64) REFERENCES drivers(driver_id),
    fare FLOAT,
    surge_multiplier FLOAT,
    tip FLOAT,
    payment_type TEXT,
    pickup_time TIMESTAMP,
    dropoff_time TIMESTAMP,
    pickup_lat FLOAT,
    pickup_lng FLOAT,
    dropoff_lat FLOAT,
    dropoff_lng FLOAT,
    weather TEXT,
    city TEXT,
    loyalty_status TEXT
);
-- TABLE 4 - PROMOTIONS TABLE
CREATE TABLE promotions (
    promo_id TEXT,
    promo_name TEXT,
    promo_type TEXT,
    promo_value FLOAT,
    start_date DATE,
    end_date DATE,
    target_segment TEXT,
    city_scope TEXT,
    ab_test_groups TEXT,  
    test_allocation TEXT,
    success_metric TEXT
);
-- TABLE 5 - SESSIONS TABLE
CREATE TABLE sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    rider_id VARCHAR(64) REFERENCES riders(user_id),
    session_time TIMESTAMP,
    time_on_app INTEGER,
    pages_visited INTEGER,
    converted BOOLEAN,
    city TEXT,
    loyalty_status TEXT
);