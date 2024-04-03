-- Sacamos las compañías
with clean_companies as (
    select companies.id as mp_id, companies.salesforce_id, companies.fiscal_name
    from companies
),
-- Sacamos los working orders
clean_wos as (
    select companyid as mp_id, count(distinct(id)) as total_wos
    from wos
    where cancelled_at is null
    group by mp_id
),
-- Sacamos los quotations
clean_quotes as (
    select manufacturing_partner_id as mp_id, count(*) as total_quotes
    from quotations
    where deleted_at is null
    group by manufacturing_partner_id
),
-- Sacamos el main process de cada uno
mps_process AS (
    select distinct companies.salesforce_id, rfqs.main_process_l0_code as main_process
    from rfqs
    left join quotations on quotations.requirementid = rfqs.id
    left join companies on quotations.manufacturing_partner_id = companies.id
    where companies.salesforce_id is not null
),
final_query as (
    select salesforce_id, total_wos as mb_wos, total_quotes as mb_quotes
    from clean_companies
    left join clean_wos on clean_wos.mp_id = clean_companies.mp_id
    left join clean_quotes on clean_quotes.mp_id = clean_companies.mp_id
    where total_wos is not null or total_quotes is not null
)
select *
from final_query
--insert_where_clause_here
--insert_order_by_clause_here