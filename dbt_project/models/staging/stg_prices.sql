
select
    time  as price_at,
    price as price_eur_mwh
from {{ source('raw', 'prices') }}
