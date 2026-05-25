with orders as (
    select * from main.stg_orders
),

zone_stats as (
    select
        district,
        count(order_id)                      as total_orders,
        round(avg(delivery_time_min), 1)     as avg_delivery_min,
        sum(is_delayed)                      as total_delayed,
        round(
            sum(is_delayed) * 100.0
            / count(order_id), 1)            as delay_rate_pct,
        round(sum(order_value_sar), 0)       as total_revenue_sar,
        sum(is_peak_hour)                    as peak_hour_orders,
        round(
            sum(is_peak_hour) * 100.0
            / count(order_id), 1)            as peak_hour_pct

    from orders
    group by district
)

select * from zone_stats
order by total_orders desc