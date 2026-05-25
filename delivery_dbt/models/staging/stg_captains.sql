with source as (
    select * from dim_captains
),

staged as (
    select
        captain_id,
        name,
        rating,
        avg_speed_kmh,
        active_hours,
        district,
        total_deliveries,
        on_time_rate,

        case
            when rating >= 4.5 then 'excellent'
            when rating >= 3.5 then 'good'
            when rating >= 2.5 then 'average'
            else 'poor'
        end as performance_tier

    from source
)

select * from staged