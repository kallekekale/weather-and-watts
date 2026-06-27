
select
    station_id,
    time as observed_at,

    max(case when parameter_name = 'TA_PT1H_AVG' then parameter_value end) as temp_c,
    max(case when parameter_name = 'WS_PT1H_AVG' then parameter_value end) as wind_speed_ms,
    max(case when parameter_name = 'WS_PT1H_MAX' then parameter_value end) as wind_gust_ms,
    max(case when parameter_name = 'WD_PT1H_AVG' then parameter_value end) as wind_direction_deg

from {{ source('raw', 'weather') }}
group by station_id, time
