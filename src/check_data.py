import duckdb

con = duckdb.connect("data/delivery.db")

print("=" * 55)
print("  DATABASE VALIDATION")
print("=" * 55)

tables = ["fact_orders", "dim_captains", "dim_restaurants"]
for table in tables:
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<25} : {count:,} rows")

print("\n" + "-" * 55)
print("  TOP 5 ORDERS SAMPLE")
print("-" * 55)

df = con.execute("""
    SELECT
        order_id,
        district,
        delivery_time_min,
        weather,
        traffic_level,
        status
    FROM fact_orders
    LIMIT 5
""").df()

print(df.to_string(index=False))

print("\n" + "-" * 55)
print("  ORDERS BY STATUS")
print("-" * 55)

df2 = con.execute("""
    SELECT
        status,
        COUNT(*) as total,
        ROUND(AVG(delivery_time_min), 1) as avg_time
    FROM fact_orders
    GROUP BY status
    ORDER BY total DESC
""").df()

print(df2.to_string(index=False))

print("\n" + "-" * 55)
print("  TOP 5 BUSIEST DISTRICTS")
print("-" * 55)

df3 = con.execute("""
    SELECT
        district,
        COUNT(*) as orders,
        ROUND(AVG(delivery_time_min), 1) as avg_delivery_min
    FROM fact_orders
    GROUP BY district
    ORDER BY orders DESC
    LIMIT 5
""").df()

print(df3.to_string(index=False))
print("=" * 55)

con.close()