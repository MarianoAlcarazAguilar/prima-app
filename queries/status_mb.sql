WITH clean_wos AS (                                                             -- Encontramos el total de working orders por MP
    SELECT companyid AS mp_id, COUNT(*) AS n_wos
    FROM wos
    WHERE cancelled_at IS NULL
    GROUP BY companyid
),
clean_quotes AS (                                                               -- Encontramos el total de quotations por MP
    SELECT manufacturing_partner_id AS mp_id, COUNT(*) AS n_quotes
    FROM quotations
    WHERE deleted_at IS NULL
    GROUP BY manufacturing_partner_id
),
clean_companies AS (                                                            -- Encontramos los valores únicos de ids para los MPs
    SELECT DISTINCT id AS mp_id, salesforce_id
    FROM companies
),
sf_status AS (                                                                  -- Tomamos los status actuales de los MPs en SF
    SELECT DISTINCT account_id AS salesforce_id, account_status AS status_quo
    FROM sf_accounts
    -- Omitimos los que sean clientes
    WHERE LOWER(account_status) LIKE '%mp%'                                    
),
assigned_status AS (                                                            -- Juntamos los valores que hemos encontrado
    SELECT clean_companies.salesforce_id,                         
        -- Asignamos el status adecuado (solo coregimos Active y Developing)
        CASE 
            WHEN n_wos IS NULL AND n_quotes IS NULL  AND status_quo in ('Active MP (working)', 'Developing MP (Quoted)' ) THEN NULL
            WHEN n_wos > 0 THEN 'Active MP (working)'
            WHEN n_quotes > 0 THEN 'Developing MP (Quoted)'
            ELSE status_quo
        END AS mb_status
    FROM clean_companies
    LEFT JOIN clean_wos ON clean_companies.mp_id = clean_wos.mp_id
    LEFT JOIN clean_quotes ON clean_companies.mp_id = clean_quotes.mp_id
    LEFT JOIN sf_status ON sf_status.salesforce_id = clean_companies.salesforce_id
    WHERE status_quo IS NOT NULL AND mb_status IS NOT NULL AND status_quo != mb_status
)
SELECT *
FROM assigned_status
--insert_where_clause_here
--insert_order_by_clause_here;