with source as (
    select * from fact_orders
),

staged as (
    select
        order_id,
        customer_id,
        captain_id,
        restaurant_id,
        district,
        order_time,
        delivery_time_min,
        prep_time_min,
        weather,
        traffic_level,
        order_value_sar,
        status,
        hour_of_day,
        day_of_week,
        is_peak_hour,
        is_delayed,

        case
            when delivery_time_min <= 30 then 'fast'
            when delivery_time_min <= 50 then 'normal'
            else 'slow'
        end as delivery_speed,

        case
            when order_value_sar >= 200 then 'high'
            when order_value_sar >= 100 then 'medium'
            else 'low'
        end as order_value_segment

    from source
)

select * from staged