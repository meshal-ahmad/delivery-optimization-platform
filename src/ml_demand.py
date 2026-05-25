import duckdb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
import os
 
print("=" * 60)
print("  Delivery Optimization Platform v1.0")
print("  ML Pipeline — Demand Forecasting Model")
print("=" * 60)
 
# ==================== LOAD DATA ====================
print("\n[1/5] Loading data from DuckDB...")
 
con = duckdb.connect("data/delivery.db")
df = con.execute("""
    SELECT
        district,
        hour_of_day,
        day_of_week,
        is_peak_hour,
        weather,
        traffic_level
    FROM fact_orders
""").df()
con.close()
 
print(f"    Loaded: {len(df):,} records")
 
# ==================== FEATURE ENGINEERING ====================
print("\n[2/5] Aggregating demand by district + hour...")
 
demand = df.groupby([
    'district',
    'hour_of_day',
    'day_of_week',
    'is_peak_hour',
    'weather',
    'traffic_level'
]).size().reset_index(name='order_count')
 
# LabelEncoder منفصل لكل عمود
categorical_cols = {
    'district'     : 'district_enc',
    'day_of_week'  : 'day_enc',
    'weather'      : 'weather_enc',
    'traffic_level': 'traffic_enc',
}
 
encoders = {}
for col, new_col in categorical_cols.items():
    le = LabelEncoder()
    demand[new_col] = le.fit_transform(demand[col])
    encoders[col] = le
 
features = [
    'district_enc',
    'hour_of_day',
    'day_enc',
    'weather_enc',
    'traffic_enc',
]

X = demand[features]
y = demand['order_count']
 
print(f"    Aggregated rows : {len(demand):,}")
print(f"    Avg orders/slot : {y.mean():.1f}")
print(f"    Max orders/slot : {y.max()}")
 
# ==================== SPLIT ====================
print("\n[3/5] Splitting data...")
 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
 
print(f"    Train : {len(X_train):,}")
print(f"    Test  : {len(X_test):,}")
 
# ==================== TRAIN ====================
print("\n[4/5] Training XGBoost Regressor...")
 
model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    random_state=42,
    verbosity=0
)
 
model.fit(X_train, y_train)
print("    Training complete!")
 
# ==================== EVALUATE ====================
print("\n[5/5] Evaluating model...")
 
y_pred = model.predict(X_test)
mae    = mean_absolute_error(y_test, y_pred)
rmse   = np.sqrt(mean_squared_error(y_test, y_pred))
 
# MAPE آمن — يتجاهل القيم الصفرية
mask = y_test > 0
mape = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100
 
print("\n" + "=" * 60)
print("  MODEL RESULTS — Demand Forecasting")
print("=" * 60)
print(f"  MAE  (Mean Absolute Error)  : {mae:.2f} orders")
print(f"  RMSE (Root Mean Sq. Error)  : {rmse:.2f} orders")
print(f"  MAPE (Mean Abs. % Error)    : {mape:.1f}%")
 
# Feature Importance
print("\n  TOP FEATURES:")
print("-" * 60)
importance = pd.Series(model.feature_importances_, index=features)
importance = importance.sort_values(ascending=False)
for feat, score in importance.items():
    bar = "█" * int(score * 100)
    print(f"  {feat:<20} {bar} {score:.3f}")
 
# ==================== SAMPLE FORECAST ====================
print("\n" + "-" * 60)
print("  SAMPLE FORECAST — Next Peak Hours")
print("-" * 60)
 
districts     = ['العليا', 'النخيل', 'الملقا', 'حطين', 'الياسمين']
district_encs = encoders['district'].transform(
    [d for d in districts if d in encoders['district'].classes_]
)
 
sample = pd.DataFrame({
    'district_enc' : district_encs,
    'hour_of_day'  : [20, 20, 13, 13, 21],
    'day_enc'      : [4,  4,  4,  4,  4],
    'weather_enc'  : [2,  2,  2,  2,  2],
    'traffic_enc'  : [2,  2,  2,  2,  2],
})
 
predictions = model.predict(sample)
for district, pred in zip(districts, predictions):
    print(f"  {district:<15} → {pred:.0f} orders expected")
 
# ==================== SAVE ====================
os.makedirs("models", exist_ok=True)
joblib.dump(model,    "models/demand_forecast_model.pkl")
joblib.dump(encoders, "models/demand_encoders.pkl")
 
print("\n" + "=" * 60)
print("  Model saved   : models/demand_forecast_model.pkl")
print("  Encoders saved: models/demand_encoders.pkl")
print("=" * 60)