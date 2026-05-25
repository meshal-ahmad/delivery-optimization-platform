import duckdb
import pandas as pd

con = duckdb.connect("data/delivery.db")

print("=" * 60)
print("  Delivery Optimization Platform v1.0")
print("  Operational Analysis Report")
print("=" * 60)

# ==================== 1. OVERVIEW ====================
print("\n[1/6] OVERVIEW")
print("-" * 60)

overview = con.execute("""
    SELECT
        COUNT(*)                                         AS total_orders,
        ROUND(AVG(delivery_time_min), 1)                AS avg_delivery_min,
        ROUND(SUM(order_value_sar), 0)                  AS total_revenue_sar,
        ROUND(AVG(order_value_sar), 1)                  AS avg_order_value,
        SUM(CASE WHEN status = 'delivered'  THEN 1 END) AS delivered,
        SUM(CASE WHEN status = 'delayed'    THEN 1 END) AS delayed,
        SUM(CASE WHEN status = 'cancelled'  THEN 1 END) AS cancelled
    FROM fact_orders
""").df()

print(f"  Total Orders      : {overview['total_orders'][0]:,}")
print(f"  Total Revenue     : {overview['total_revenue_sar'][0]:,.0f} SAR")
print(f"  Avg Order Value   : {overview['avg_order_value'][0]} SAR")
print(f"  Avg Delivery Time : {overview['avg_delivery_min'][0]} min")
print(f"  Delivered         : {overview['delivered'][0]:,}")
print(f"  Delayed           : {overview['delayed'][0]:,}")
print(f"  Cancelled         : {overview['cancelled'][0]:,}")

# ==================== 2. BUSIEST DISTRICTS ====================
print("\n[2/6] TOP 5 BUSIEST DISTRICTS")
print("-" * 60)

districts = con.execute("""
    SELECT
        district,
        COUNT(*)                                AS total_orders,
        ROUND(AVG(delivery_time_min), 1)        AS avg_time,
        SUM(CASE WHEN is_delayed = 1 THEN 1
            ELSE 0 END)                         AS delayed_orders,
        ROUND(
            SUM(CASE WHEN is_delayed = 1
                THEN 1 ELSE 0 END) * 100.0
            / COUNT(*), 1)                      AS delay_rate_pct
    FROM fact_orders
    GROUP BY district
    ORDER BY total_orders DESC
    LIMIT 5
""").df()

print(districts.to_string(index=False))

# ==================== 3. WEATHER IMPACT ====================
print("\n[3/6] WEATHER IMPACT ON DELIVERY")
print("-" * 60)

weather = con.execute("""
    SELECT
        weather,
        COUNT(*)                                AS orders,
        ROUND(AVG(delivery_time_min), 1)        AS avg_time,
        ROUND(
            SUM(CASE WHEN is_delayed = 1
                THEN 1 ELSE 0 END) * 100.0
            / COUNT(*), 1)                      AS delay_rate_pct
    FROM fact_orders
    GROUP BY weather
    ORDER BY avg_time DESC
""").df()

print(weather.to_string(index=False))

# ==================== 4. PEAK HOURS ====================
print("\n[4/6] ORDERS BY HOUR (TOP 8)")
print("-" * 60)

hours = con.execute("""
    SELECT
        hour_of_day,
        COUNT(*)                                AS orders,
        ROUND(AVG(delivery_time_min), 1)        AS avg_time,
        ROUND(
            SUM(CASE WHEN is_delayed = 1
                THEN 1 ELSE 0 END) * 100.0
            / COUNT(*), 1)                      AS delay_rate_pct
    FROM fact_orders
    GROUP BY hour_of_day
    ORDER BY orders DESC
    LIMIT 8
""").df()

print(hours.to_string(index=False))

# ==================== 5. CAPTAIN PERFORMANCE ====================
print("\n[5/6] TOP 5 WORST CAPTAINS (by delay rate)")
print("-" * 60)

captains = con.execute("""
    SELECT
        c.captain_id,
        c.rating,
        COUNT(o.order_id)                       AS total_orders,
        ROUND(AVG(o.delivery_time_min), 1)      AS avg_time,
        ROUND(
            SUM(CASE WHEN o.is_delayed = 1
                THEN 1 ELSE 0 END) * 100.0
            / COUNT(*), 1)                      AS delay_rate_pct
    FROM fact_orders o
    JOIN dim_captains c ON o.captain_id = c.captain_id
    GROUP BY c.captain_id, c.rating
    HAVING COUNT(o.order_id) >= 50
    ORDER BY delay_rate_pct DESC
    LIMIT 5
""").df()

print(captains.to_string(index=False))

# ==================== 6. RESTAURANT PERFORMANCE ====================
print("\n[6/6] TOP 5 WORST RESTAURANTS (by avg prep time)")
print("-" * 60)

restaurants = con.execute("""
    SELECT
        r.name,
        r.cuisine_type,
        COUNT(o.order_id)                       AS total_orders,
        ROUND(AVG(o.prep_time_min), 1)          AS avg_prep_min,
        ROUND(AVG(o.delivery_time_min), 1)      AS avg_total_min,
        ROUND(
            SUM(CASE WHEN o.is_delayed = 1
                THEN 1 ELSE 0 END) * 100.0
            / COUNT(*), 1)                      AS delay_rate_pct
    FROM fact_orders o
    JOIN dim_restaurants r ON o.restaurant_id = r.restaurant_id
    GROUP BY r.name, r.cuisine_type
    ORDER BY avg_prep_min DESC
    LIMIT 5
""").df()

print(restaurants.to_string(index=False))

print("\n" + "=" * 60)
print("  ANALYSIS COMPLETE")
print("=" * 60)

con.close() 
