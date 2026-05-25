
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
        o.hour_of_day,
        o.is_peak_hour,
        o.order_value_sar,
        o.weather,
        o.traffic_level,
        o.day_of_week,
        o.district,
        c.rating            AS captain_rating,
        c.avg_speed_kmh     AS captain_speed,
        r.cuisine_type,
        o.is_delayed
    FROM fact_orders o
    JOIN dim_captains    c ON o.captain_id    = c.captain_id
    JOIN dim_restaurants r ON o.restaurant_id = r.restaurant_id
""").df()
con.close()
 
print(f"    Loaded : {len(df):,} records")
print(f"    Delayed: {df['is_delayed'].sum():,} ({df['is_delayed'].mean()*100:.1f}%)")
 
# ==================== FEATURE ENGINEERING ====================
print("\n[2/5] Feature engineering...")
 
# استخدام LabelEncoder منفصل لكل عمود
categorical_cols = {
    'weather'      : 'weather_enc',
    'traffic_level': 'traffic_enc',
    'day_of_week'  : 'day_enc',
    'district'     : 'district_enc',
    'cuisine_type' : 'cuisine_enc',
}
 
encoders = {}
for col, new_col in categorical_cols.items():
    le = LabelEncoder()
    df[new_col] = le.fit_transform(df[col])
    encoders[col] = le  # حفظ كل encoder منفصل
 
features = [
    'hour_of_day',
    'is_peak_hour',
    'order_value_sar',
    'captain_rating',
    'captain_speed',
    'weather_enc',
    'traffic_enc',
    'day_enc',
    'district_enc',
    'cuisine_enc',
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
 
print(f"    Train: {len(X_train):,}")
print(f"    Test : {len(X_test):,}")
 
# ==================== TRAIN ====================
print("\n[4/5] Training XGBoost model...")
 
# معالجة class imbalance
ratio = (y == 0).sum() / (y == 1).sum()
print(f"    Class ratio (0/1): {ratio:.2f} → scale_pos_weight={ratio:.2f}")
 
model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    scale_pos_weight=ratio,
    random_state=42,
    eval_metric='logloss',
    verbosity=0
)
 
model.fit(X_train, y_train)
print("    Training complete!")
 
# ==================== EVALUATE ====================
print("\n[5/5] Evaluating model...")
 
y_pred = model.predict(X_test)
 
report    = classification_report(y_test, y_pred, output_dict=True)
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
 
# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("\n  CONFUSION MATRIX:")
print("-" * 60)
print(f"  TN: {cm[0][0]:,}  FP: {cm[0][1]:,}")
print(f"  FN: {cm[1][0]:,}  TP: {cm[1][1]:,}")
 
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
joblib.dump(model,    "models/delay_prediction_model.pkl")
joblib.dump(features, "models/features.pkl")
joblib.dump(encoders, "models/encoders.pkl")
 
print("\n" + "=" * 60)
print("  Model saved   : models/delay_prediction_model.pkl")
print("  Encoders saved: models/encoders.pkl")
print("=" * 60)
 