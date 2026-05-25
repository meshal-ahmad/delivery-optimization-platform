with source as (
    select * from dim_restaurants
),

staged as (
    select
        restaurant_id,
        name,
        cuisine_type,
        avg_prep_time_min,
        rating,
        district,
        total_orders,
        
        case
            when avg_prep_time_min <= 10 then 'fast'
            when avg_prep_time_min <= 20 then 'normal'
            else 'slow'
        end as prep_speed_tier

    from source
)

select * from staged