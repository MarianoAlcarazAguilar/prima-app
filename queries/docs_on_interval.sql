with quotes as (
    select quotations.id as doc_id, quotations.created_at as doc_date, companies.salesforce_id as mp_id, 'quotes' as tipo
    from quotations
    join companies on companies.id = quotations.manufacturing_partner_id
    where quotations.manufacturing_partner_id is not null and quotations.deleted_at is null
),
working_orders as (
    select wos.id as doc_id, wos.created_at as doc_date, companies.salesforce_id as mp_id, 'wos' as tipo
    from wos
    join companies on companies.id = wos.companyid
    where wos.companyid is not null and wos.cancelled_at is null
)
select * from working_orders
union all 
select * from quotes
--insert_where_clause_here
--insert_order_by_clause_here