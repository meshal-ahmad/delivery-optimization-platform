import duckdb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
import os

print("=" * 60)
print("  Delivery Optimization Platform v1.0")
print("  ML Pipeline — Delay Prediction Model")
print("=" * 60)

# ==================== LOAD DATA ====================
print("\n[1/5] Loading data from DuckDB...")

con = duckdb.connect("data/delivery.db")
df = con.execute("""
    SELECT
        o.delivery_time_min,
        o.prep_time_min,
        o.hour_of_day,
        o.is_peak_hour,
        o.order_value_sar,
        o.weather,
        o.traffic_level,
        o.day_of_week,
        o.district,
        c.rating         as captain_rating,
        c.avg_speed_kmh  as captain_speed,
        r.avg_prep_time_min as restaurant_avg_prep,
        r.cuisine_type,
        o.is_delayed
    FROM fact_orders o
    JOIN dim_captains c    ON o.captain_id    = c.captain_id
    JOIN dim_restaurants r ON o.restaurant_id = r.restaurant_id
""").df()
con.close()

print(f"    Loaded: {len(df):,} records")
print(f"    Delayed: {df['is_delayed'].sum():,} ({df['is_delayed'].mean()*100:.1f}%)")

# ==================== FEATURE ENGINEERING ====================
print("\n[2/5] Feature engineering...")

le = LabelEncoder()
df['weather_enc']      = le.fit_transform(df['weather'])
df['traffic_enc']      = le.fit_transform(df['traffic_level'])
df['day_enc']          = le.fit_transform(df['day_of_week'])
df['district_enc']     = le.fit_transform(df['district'])
df['cuisine_enc']      = le.fit_transform(df['cuisine_type'])

features = [
    'prep_time_min',
    'hour_of_day',
    'is_peak_hour',
    'order_value_sar',
    'captain_rating',
    'captain_speed',
    'restaurant_avg_prep',
    'weather_enc',
    'traffic_enc',
    'day_enc',
    'district_enc',
    'cuisine_enc'
]

X = df[features]
y = df['is_delayed']

print(f"    Features: {len(features)}")
print(f"    Samples : {len(X):,}")

# ==================== SPLIT ====================
print("\n[3/5] Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"    Train : {len(X_train):,}")
print(f"    Test  : {len(X_test):,}")

# ==================== TRAIN ====================
print("\n[4/5] Training XGBoost model...")

model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    random_state=42,
    eval_metric='logloss',
    verbosity=0
)

model.fit(X_train, y_train)
print("    Training complete!")

# ==================== EVALUATE ====================
print("\n[5/5] Evaluating model...")

y_pred = model.predict(X_test)

report = classification_report(y_test, y_pred, output_dict=True)
accuracy  = report['accuracy']
precision = report['1']['precision']
recall    = report['1']['recall']
f1        = report['1']['f1-score']

print("\n" + "=" * 60)
print("  MODEL RESULTS — Delay Prediction")
print("=" * 60)
print(f"  Accuracy  : {accuracy*100:.1f}%")
print(f"  Precision : {precision*100:.1f}%")
print(f"  Recall    : {recall*100:.1f}%")
print(f"  F1 Score  : {f1*100:.1f}%")

# Feature Importance
print("\n  TOP 5 IMPORTANT FEATURES:")
print("-" * 60)
importance = pd.Series(model.feature_importances_, index=features)
importance = importance.sort_values(ascending=False).head(5)
for feat, score in importance.items():
    bar = "█" * int(score * 100)
    print(f"  {feat:<25} {bar} {score:.3f}")

# ==================== SAVE MODEL ====================
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/delay_prediction_model.pkl")
joblib.dump(features, "models/features.pkl")

print("\n" + "=" * 60)
print("  Model saved: models/delay_prediction_model.pkl")
print("=" * 60)