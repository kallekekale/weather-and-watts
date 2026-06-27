-- Pivot FMI weather from long format (one row per station/time/parameter)
-- into wide format (one row per station/time, parameters as columns).
-- MAX(CASE ...) works because there is exactly one row per parameter per
-- group, and MAX ignores the NULLs the CASE produces for non-matching rows.

select
    station_id,
    time as observed_at,

    max(case when parameter_name = 'TA_PT1H_AVG' then parameter_value end) as temp_c,
    max(case when parameter_name = 'WS_PT1H_AVG' then parameter_value end) as wind_speed_ms,
    max(case when parameter_name = 'WS_PT1H_MAX' then parameter_value end) as wind_gust_ms,
    max(case when parameter_name = 'WD_PT1H_AVG' then parameter_value end) as wind_direction_deg

from {{ source('raw', 'weather') }}
group by station_id, time
