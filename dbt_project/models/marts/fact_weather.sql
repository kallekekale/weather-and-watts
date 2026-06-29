select
    station_id,
    date_trunc('hour', observed_at) as observed_hour,
    avg(temp_c)             as temp_c,
    avg(wind_speed_ms)      as wind_speed_ms,
    avg(wind_gust_ms)       as wind_gust_ms,
    avg(wind_direction_deg) as wind_direction_deg
from {{ ref('stg_weather') }}
group by 1, 2
