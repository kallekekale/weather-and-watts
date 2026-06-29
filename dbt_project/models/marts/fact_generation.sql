select
    series, 
    date_trunc('hour', generation_start) as generation_hour,
    avg(value_mw) as average_mw

from {{ ref('stg_generation') }}
group by 1, 2
