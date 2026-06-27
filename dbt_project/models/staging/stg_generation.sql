select
    dataset_id,
    start_time as generation_start,
    end_time as generation_end,
    value as value_mw,

    case dataset_id
        when 75  then 'wind_production'
        when 193 then 'total_consumption'
        when 245 then 'wind_forecast'
    end as series


from {{ source('raw', 'generation') }}
