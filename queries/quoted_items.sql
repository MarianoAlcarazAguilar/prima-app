-- Sacamos la info necesaria de los RFQs
with rfqs_data as (
    select 
        rfqs.id as rfq_id, 
        rfqs.name as rfq_name, 
        rfqs.main_process_l0_code as main_process, 
        rfqs.pod_code as pod, 
        companies.fiscal_name as customer_name, 
        companies.id as customer_id,
        companies.salesforce_id as customer_sf_id
    from rfqs
    left join companies on companies.id = rfqs.customer_id
    where rfqs.pod_code != 'Raw Materials'
),
-- Sacamos la info necesaria de los Quotations
quotes_data as (
    select 
        quotations.id as quote_id, 
        quotations.requirementid as rfq_id, 
        quotations.manufacturing_partner_id as mp_id, 
        quotations.created_at as quote_date, 
        quotations.currency as quote_currency
    from quotations
    where 
        quotations.type != 'Customer' and -- no buscamos los quotes de customer (pensando que luego habrá de pricing model)
        deleted_at is Null 
),
-- Sacamos info del target price de los itesm
target_prices as (
    select 
        id as target_price_id, 
        name as item_id, 
        quantity as target_quantity, 
        requirement_id as rfq_id, 
        currency as target_currency, 
        unit_target_price as target_price
    from items_requirements
    where deleted_at is Null
),
-- Sacamos la info de los Items
items_data as (
    select 
        items_quotation.quotation_id as quote_id, 
        items_quotation.name as item_id, 
        items_quotation.unit_price, 
        items_quotation.id as item_quote_id, 
        items_quotation.quantity as quoted_cuantity,
        unit_code
    from items_quotation
    where deleted_at is Null -- 
    and unit_price != 0 -- no queremos meter los productos cuando aún no los han subido
),
companies_data as (
    select 
        id as mp_id, 
        salesforce_id as mp_sf_id, 
        fiscal_name as mp_name
    from companies
),
-- Juntamos los datos
final_query as (
    select 
        items_data.item_quote_id as name, 
        --rfqs_data.customer_id,
        rfqs_data.rfq_id as rfq_id__c, 
        --quotes_data.quote_id, 
        --quotes_data.mp_id, 
        companies_data.mp_sf_id as mp_account__c, 
        --rfqs_data.customer_sf_id,
        --companies_data.mp_name, 
        rfqs_data.rfq_name as rfq_name__c, 
        rfqs_data.customer_name as customer_name__c,
        rfqs_data.main_process as main_process__c, 
        rfqs_data.pod as pod__c, 
        items_data.item_id as item_name__c, 
        quotes_data.quote_currency as quote_currency__c, 
        --items_data.unit_code,
        items_data.unit_price as quote_price__c,
        --items_data.quoted_cuantity,
        --target_prices.target_quantity,
        target_prices.target_currency as target_currency__c,
        target_prices.target_price as target_price__c
    from rfqs_data
    inner join quotes_data on quotes_data.rfq_id = rfqs_data.rfq_id
    inner join items_data on items_data.quote_id = quotes_data.quote_id
    inner join target_prices on target_prices.rfq_id = rfqs_data.rfq_id and target_prices.item_id = items_data.item_id
    left join companies_data on companies_data.mp_id = quotes_data.mp_id
)
select *
from final_query
--insert_where_clause_here
--insert_order_by_clause_here