-- The simplest possible staging model: read the raw price rows, rename the
-- columns to clearer names, and expose them as a clean view.

select
    time  as price_at,
    price as price_eur_mwh
from {{ source('raw', 'prices') }}
