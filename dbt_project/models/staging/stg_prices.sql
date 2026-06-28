select
    time                                  as price_at,
    time at time zone 'Europe/Helsinki'   as price_at_local,
    price                                 as price_eur_mwh
from {{ source('raw', 'prices') }}
