-- Vamos a identificar el número de veces que los MPs han participado en cada proceso
-- Quiero tener las siguientes columnas: mp, process, count

-- Primero tomamos los rfqs y sus correspondientes process
with rfq_main_process as (
    select distinct id as rfq_id, main_process_l0_code as main_process 
    from rfqs
    where main_process_l0_code is not null
),
-- Segundo: tomamos los quotes que se han hecho para los rfqs
quotes_done_by_mps as (
    select id as quote_id, requirementid as rfq_id, manufacturing_partner_id as mp_id
    from quotations
    where deleted_at is null and manufacturing_partner_id is not null
),
-- Tercero: tomamos los wos que se han hecho para los rfqs
wos_done_by_mps as (
    select wos.id as wo_id, companyid as mp_id, pos.requirement_id as rfq_id
    from wos
    left join pos on pos.id = wos.purchase_order_id
    where wos.cancelled_at is null
),
-- Cuarto: contamos cuántos quotes han hecho para cada main_process
quotes_process_count as (
    select mp_id, main_process, count(*) as total_quotes_done
    from quotes_done_by_mps
    left join rfq_main_process on rfq_main_process.rfq_id = quotes_done_by_mps.rfq_id
    group by mp_id, main_process
),
-- Quinto: contamos cuántos wos han hecho para cada main_process
wos_process_count as (
    select mp_id, main_process, count(*) as total_wos_done
    from wos_done_by_mps
    left join rfq_main_process on rfq_main_process.rfq_id = wos_done_by_mps.rfq_id
    group by mp_id, main_process
),
-- Sexto: juntamos total quotes y total wos
total_wos_quotes as (
    select  
        case 
            when quotes_process_count.mp_id is null then wos_process_count.mp_id
            else quotes_process_count.mp_id
        end as mp_id,
        case
            when quotes_process_count.main_process is null then wos_process_count.main_process
            else quotes_process_count.main_process
        end as main_process,
        total_wos_done, total_quotes_done
    from wos_process_count
    full outer join quotes_process_count on quotes_process_count.mp_id = wos_process_count.mp_id and quotes_process_count.main_process = wos_process_count.main_process
),
-- Les ponemos nombres y sf_id
final_query as (
    select companies.salesforce_id as salesforce_id, companies.fiscal_name as mp_name,  main_process, total_wos_done as total_wos, total_quotes_done as total_quotes
    from total_wos_quotes
    left join companies on companies.id = total_wos_quotes.mp_id
)
select *
from final_query
--insert_where_clause_here
--insert_order_by_clause_here
;



