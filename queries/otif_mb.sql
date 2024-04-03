WITH delivery_outcomes AS (
    SELECT *,
        CASE
            WHEN in_full ILIKE 't%' AND on_time ILIKE 't%' THEN 1 ELSE 0
        END AS otif
    FROM purchase_order_deliveries
    WHERE status = 'Fulfilled'
),
otif_calculations AS (
    SELECT 
        companies.salesforce_id,
        AVG(CAST(delivery_outcomes.otif AS FLOAT)) * 100 AS otif
    FROM  wos 
    LEFT JOIN delivery_outcomes ON wos.purchase_order_id = delivery_outcomes.purchase_order_id
    LEFT JOIN companies ON wos.companyid = companies.id
    GROUP BY companies.salesforce_id
),
final_query AS (
    SELECT *
    FROM otif_calculations AS oc
    WHERE oc.otif IS NOT NULL
)
SELECT *
FROM final_query
--insert_where_clause_here
--insert_order_by_clause_here
;