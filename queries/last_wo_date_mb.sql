with last_wos as (
    select companyid, max(created_at) as date_last_wo
    from wos
    where cancelled_at is null
    group by companyid
), 
latest_wos as (
    select salesforce_id as sf_id, date_last_wo
    from companies
    right join last_wos on last_wos.companyid = companies.id
)
select *
from latest_wos
--insert_where_clause_here
--insert_order_by_clause_here