import duckdb
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker('ar_SA')
random.seed(99)

# ==================== CONFIG ====================
NUM_ORDERS      = 50000
NUM_CAPTAINS    = 200
NUM_RESTAURANTS = 80
START_DATE      = datetime(2025, 1, 1)
END_DATE        = datetime(2026, 5, 23)

DISTRICTS = [
    "العليا", "النخيل", "الملقا", "حطين", "الياسمين",
    "الورود", "السليمانية", "المروج", "الربوة", "الشهداء"
]

WEATHER    = ["صافي", "غائم", "عاصف", "حار جداً", "بارد"]
TRAFFIC    = ["خفيف", "متوسط", "كثيف", "شديد الكثافة"]
CUISINE    = ["برغر", "مندي", "بيتزا", "سوشي", "مشاوي", "فراخ", "حلويات"]
PEAK_HOURS = [12, 13, 19, 20, 21]

# ==================== DELAY LOGIC ====================
def calculate_delay(prep, delivery, weather, traffic, hour, captain_rating):
    total = prep + delivery

    if weather == "عاصف":
        total += random.randint(5, 10)
    elif weather == "حار جداً":
        total += random.randint(2, 5)

    if traffic == "شديد الكثافة":
        total += random.randint(8, 12)
    elif traffic == "كثيف":
        total += random.randint(3, 7)

    if hour in PEAK_HOURS:
        total += random.randint(3, 8)

    if captain_rating < 3.5:
        total += random.randint(2, 5)

    return total

# ==================== STATUS LOGIC ====================
def calculate_status(total_minutes, weather, traffic):
    cancel_chance = 0.05

    if weather == "عاصف":
        cancel_chance += 0.04
    if traffic == "شديد الكثافة":
        cancel_chance += 0.03
    if total_minutes > 60:
        cancel_chance += 0.05

    if random.random() < cancel_chance:
        return "cancelled"
    elif total_minutes > 50:
        return "delayed"
    else:
        return "delivered"

print("=" * 55)
print("  Delivery Optimization Platform v1.0")
print("  Generating 50,000 orders...")
print("=" * 55)

# ==================== CAPTAINS ====================
print("\n[1/5] Generating captains...")
captains = []
for i in range(1, NUM_CAPTAINS + 1):
    captains.append({
        "captain_id"       : f"CAP{i:03d}",
        "name"             : fake.name(),
        "rating"           : round(random.uniform(2.5, 5.0), 1),
        "avg_speed_kmh"    : random.randint(20, 60),
        "active_hours"     : random.randint(4, 12),
        "district"         : random.choice(DISTRICTS),
        "total_deliveries" : random.randint(50, 5000),
        "on_time_rate"     : round(random.uniform(0.60, 0.99), 2)
    })
df_captains = pd.DataFrame(captains)
print(f"    Captains generated: {len(df_captains)}")

# ==================== RESTAURANTS ====================
print("[2/5] Generating restaurants...")
restaurants = []
for i in range(1, NUM_RESTAURANTS + 1):
    restaurants.append({
        "restaurant_id"     : f"REST{i:03d}",
        "name"              : f"مطعم {fake.last_name()}",
        "cuisine_type"      : random.choice(CUISINE),
        "avg_prep_time_min" : random.randint(5, 35),
        "rating"            : round(random.uniform(2.5, 5.0), 1),
        "district"          : random.choice(DISTRICTS),
        "total_orders"      : random.randint(100, 10000)
    })
df_restaurants = pd.DataFrame(restaurants)
print(f"    Restaurants generated: {len(df_restaurants)}")

# ==================== ORDERS ====================
print("[3/5] Generating orders (this may take a moment)...")
orders          = []
captain_list    = df_captains.to_dict("records")
restaurant_list = df_restaurants.to_dict("records")

for i in range(1, NUM_ORDERS + 1):
    captain    = random.choice(captain_list)
    restaurant = random.choice(restaurant_list)
    order_time = START_DATE + timedelta(
        seconds=random.randint(0, int((END_DATE - START_DATE).total_seconds()))
    )

    prep_time     = restaurant["avg_prep_time_min"] + random.randint(-3, 5)
    prep_time     = max(5, prep_time)
    delivery_time = random.randint(10, 35)
    weather       = random.choice(WEATHER)
    traffic       = random.choice(TRAFFIC)
    hour          = order_time.hour

    total_minutes = calculate_delay(
        prep_time, delivery_time,
        weather, traffic,
        hour, captain["rating"]
    )
    status = calculate_status(total_minutes, weather, traffic)

    orders.append({
        "order_id"          : f"ORD{i:06d}",
        "customer_id"       : f"CUST{random.randint(1, 5000):05d}",
        "captain_id"        : captain["captain_id"],
        "restaurant_id"     : restaurant["restaurant_id"],
        "district"          : random.choice(DISTRICTS),
        "order_time"        : order_time.strftime("%Y-%m-%d %H:%M:%S"),
        "delivery_time_min" : total_minutes,
        "prep_time_min"     : prep_time,
        "weather"           : weather,
        "traffic_level"     : traffic,
        "order_value_sar"   : round(random.uniform(15, 350), 2),
        "status"            : status,
        "hour_of_day"       : hour,
        "day_of_week"       : order_time.strftime("%A"),
        "is_peak_hour"      : 1 if hour in PEAK_HOURS else 0,
        "is_delayed"        : 1 if total_minutes > 50 else 0
    })

    if i % 10000 == 0:
        print(f"    Progress: {i:,} / {NUM_ORDERS:,} orders")

df_orders = pd.DataFrame(orders)
print(f"    Orders generated: {len(df_orders):,}")

# ==================== SAVE CSV ====================
print("[4/5] Saving CSV files...")
os.makedirs("data/raw", exist_ok=True)
df_orders.to_csv("data/raw/orders.csv",           index=False)
df_captains.to_csv("data/raw/captains.csv",       index=False)
df_restaurants.to_csv("data/raw/restaurants.csv", index=False)
print("    CSV files saved to data/raw/")

# ==================== SAVE DUCKDB ====================
print("[5/5] Saving to DuckDB...")
con = duckdb.connect("data/delivery.db")
con.execute("DROP TABLE IF EXISTS fact_orders")
con.execute("DROP TABLE IF EXISTS dim_captains")
con.execute("DROP TABLE IF EXISTS dim_restaurants")
con.execute("CREATE TABLE fact_orders     AS SELECT * FROM df_orders")
con.execute("CREATE TABLE dim_captains    AS SELECT * FROM df_captains")
con.execute("CREATE TABLE dim_restaurants AS SELECT * FROM df_restaurants")
con.close()

# ==================== SUMMARY ====================
delivered = df_orders[df_orders["status"] == "delivered"].shape[0]
delayed   = df_orders[df_orders["status"] == "delayed"].shape[0]
cancelled = df_orders[df_orders["status"] == "cancelled"].shape[0]
avg_time  = df_orders["delivery_time_min"].mean()
avg_value = df_orders["order_value_sar"].mean()

print("\n" + "=" * 55)
print("  PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 55)
print(f"  Total Orders       : {len(df_orders):,}")
print(f"  Delivered          : {delivered:,}  ({delivered/len(df_orders)*100:.1f}%)")
print(f"  Delayed            : {delayed:,}   ({delayed/len(df_orders)*100:.1f}%)")
print(f"  Cancelled          : {cancelled:,}   ({cancelled/len(df_orders)*100:.1f}%)")
print(f"  Avg Delivery Time  : {avg_time:.1f} min")
print(f"  Avg Order Value    : {avg_value:.1f} SAR")
print(f"  CSV saved          : data/raw/")
print(f"  Database saved     : data/delivery.db")
print("=" * 55)
