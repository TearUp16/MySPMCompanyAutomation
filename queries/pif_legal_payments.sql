SELECT
    `client`.`client_name` AS `CLIENT NAME`,
    TRIM(
        CASE
            WHEN `leads`.`leads_placement` IS NOT NULL AND `leads`.`leads_placement` != '' 
                THEN `leads`.`leads_placement`
            WHEN dv1.dynamic_value_name IS NOT NULL AND dv1.dynamic_value_name != '' 
                THEN dv1.dynamic_value_name
            ELSE 'UNPLACED '
        END
    ) AS `BRANCH`,
    leads.`leads_acctno` AS 'ACCOUNT NUMBER',
    leads.`leads_chcode` AS 'LEADS CHCODE',
    leads.`leads_chname` AS 'FULL NAME',
    users.`users_username` AS 'AGENTS',
    dv2.`dynamic_value_name` AS 'ACCOUNT TYPE',
    leads.`leads_endo_date` AS 'ENDORSE DATE',
    leads_result.`leads_result_comment` AS 'REMARKS',
    leads_result.`leads_result_ornumber` AS 'OR NUMBER',
    leads_status.`leads_status_name` AS 'STATUS',
    leads_substatus.`leads_substatus_name` AS 'SUBSTATUS',
    leads_result.`leads_result_amount` AS 'PAYMENT AMOUNT',

    -- 🔹 Format PAYMENT DATE to MM-DD-YYYY
    DATE_FORMAT(leads_result.`leads_result_sdate`, '%m-%d-%Y') AS 'PAYMENT DATE',

    -- 🔹 Format LATEST REMARKS DATE to MM/DD/YYYY h:mm AM/PM
    DATE_FORMAT(leads_result.`leads_result_barcode_date`, '%m/%d/%Y %r') AS 'LATEST REMARKS DATE',

    CONCAT(
        `leads`.`leads_chcode`, '-', 
        `leads_status`.`leads_status_name`, '-',
        `leads_substatus`.`leads_substatus_name`, '-',
        IFNULL(`leads_result`.`leads_result_ornumber`, '1'), '-',
        MONTH(`leads_result`.`leads_result_sdate`)
    ) AS `unique_combination`

FROM `bcrm`.`leads_result`
    INNER JOIN `bcrm`.`leads`
        ON `leads_result`.`leads_result_lead` = `leads`.`leads_id`
    INNER JOIN `bcrm`.`leads_status`
        ON `leads_result`.`leads_result_status_id` = `leads_status`.`leads_status_id`
    INNER JOIN `bcrm`.`leads_substatus`
        ON `leads_result`.`leads_result_substatus_id` = `leads_substatus`.`leads_substatus_id`
    INNER JOIN `bcrm`.`client`
        ON `leads`.`leads_client_id` = `client`.`client_id`
    INNER JOIN `bcrm`.`users`
        ON `users`.`users_id` = `leads_result`.`leads_result_users`
    LEFT JOIN `bcrm`.`dynamic_value` AS dv1 
        ON dv1.`dynamic_value_lead_id` = `leads`.`leads_id` 
        AND dv1.`dynamic_value_dynamic_id` = 5872
    LEFT JOIN `bcrm`.`dynamic_value` AS dv2 
        ON dv2.`dynamic_value_lead_id` = `leads`.`leads_id` 
        AND dv2.`dynamic_value_dynamic_id` = 2778                   

WHERE `client`.`client_name` = 'PIF LEGAL'
    AND `leads_result`.`leads_result_hidden` <> 1
    AND `users`.`users_username` NOT LIKE 'POUT'
    -- AND leads.`leads_endo_date` >= '2025-01-01'
    -- AND `leads_status`.`leads_status_name` LIKE 'Payment'
    AND `leads_result`.`leads_result_amount` IS NOT NULL
    AND `leads_result`.`leads_result_amount` != ''
    AND leads_result.leads_result_sdate BETWEEN ? AND ?
    AND `leads_status`.`leads_status_name` = ?

GROUP BY
    `unique_combination`

ORDER BY `leads_result`.`leads_result_barcode_date` DESC;
