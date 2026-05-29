with orders as (
    select * from PUBLIC.stg_orders
),

captains as (
    select * from PUBLIC.stg_captains
),

captain_stats as (
    select
        o.captain_id,
        c.name,
        c.rating,
        c.performance_tier,
        c.district,
        c.total_deliveries,

        count(o.order_id)                    as total_orders,
        round(avg(o.delivery_time_min), 1)   as avg_delivery_min,
        sum(o.is_delayed)                    as total_delayed,
        round(
            sum(o.is_delayed) * 100.0
            / count(o.order_id), 1)          as delay_rate_pct,
        round(sum(o.order_value_sar), 0)     as total_revenue_sar,
        round(avg(o.order_value_sar), 1)     as avg_order_value,
        sum(o.is_peak_hour)                  as peak_hour_orders

    from orders o
    left join captains c on o.captain_id = c.captain_id
    group by
        o.captain_id, c.name, c.rating,
        c.performance_tier, c.district, c.total_deliveries
)

select * from captain_stats
order by delay_rate_pct desc