select
    date_trunc('hour', price_at) as price_hour,
    avg(price_eur_mwh) as average_price_eur_mwh
from {{ ref('stg_prices') }}
group by 1
