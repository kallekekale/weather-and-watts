with price as (
    select
        price_hour as hour,
        average_price_eur_mwh
    from {{ ref('fact_price') }}
),

generation as (
    select
        generation_hour as hour,
        max(case when series = 'wind_production'   then average_mw end) as wind_production_mw,
        max(case when series = 'total_consumption' then average_mw end) as total_consumption_mw,
        max(case when series = 'wind_forecast'     then average_mw end) as wind_forecast_mw
    from {{ ref('fact_generation') }}
    group by 1
),

weather as (
    select
        observed_hour as hour,
        avg(temp_c)             as temp_c,
        avg(wind_speed_ms)      as wind_speed_ms,
        avg(wind_gust_ms)       as wind_gust_ms,
        avg(wind_direction_deg) as wind_direction_deg
    from {{ ref('fact_weather') }}
    group by 1
)

select
    price.hour,
    price.average_price_eur_mwh,
    generation.wind_production_mw,
    generation.total_consumption_mw,
    generation.wind_forecast_mw,
    weather.temp_c,
    weather.wind_speed_ms,
    weather.wind_gust_ms,
    weather.wind_direction_deg
from price
left join generation on generation.hour = price.hour
left join weather    on weather.hour    = price.hour
