SELECT 
    client.`client_name` AS 'CLIENT NAME',     
    leads.`leads_chcode` AS 'LEADS CHCODE',
    users.`users_username` AS 'USERS USERNAME', 
    leads.`leads_acctno` AS 'ACCOUNT NUMBER',
    leads.`leads_chname` AS 'FULL NAME',
    leads.`leads_email` AS 'EMAIL ADDRESS',
    #leads.`leads_birthday` AS 'BIRTH DATE',
    LEFT(leads.`leads_mobile_phone`, 11) AS 'MOBILE NUMBER',
    leads_status.`leads_status_name` AS 'STATUS',
    leads_substatus.`leads_substatus_name` AS 'SUBSTATUS',
    leads.`leads_full_address` AS 'PRIMARY ADDRESS', 
    leads.`leads_full_saddress` AS 'SECONDARY ADDRESS', 
    leads.`leads_full_taddress` AS 'TERTIARY ADDRESS',
    dv6.`dynamic_value_name` AS 'ACCOUNT TYPE',
    leads.`leads_endo_date` AS 'ENDORSE DATE',
    leads.`leads_cutoff` AS 'PULL OUT DATE',
        TRIM(
            CASE
                WHEN `leads`.`leads_placement` IS NOT NULL
                AND `leads`.`leads_placement` != '' 

                    THEN CASE 
                    WHEN `leads`.`leads_placement` LIKE '%LEGAL%'
                        THEN `leads`.`leads_placement`
                    ELSE CONCAT(`leads`.`leads_placement`, ' LEGAL')
                END

                WHEN dv7.dynamic_value_name IS NOT NULL 
                AND dv7.dynamic_value_name != ''
                    THEN CASE 
                    WHEN dv7.dynamic_value_name LIKE '%LEGAL%'
                        THEN dv7.dynamic_value_name
                    ELSE CONCAT(dv7.dynamic_value_name, ' LEGAL')
                    
                    END
                ELSE 'UNPLACED '
            END
        ) AS `PLACEMENT`,
    leads.`leads_prin` AS 'AMOUNT DUE',
    leads.`leads_ob` AS 'OUT BALANCE',
    dv1.`dynamic_value_name` AS 'TCT NO',
    dv2.`dynamic_value_name` AS 'AUCTION DATE',
    dv3.`dynamic_value_name` AS 'ANNOTATION DATE',
    dv4.`dynamic_value_name` AS 'ACCOUNT DPD',
    dv5.`dynamic_value_name` AS 'PIF OFFICE ADDRESS',
    leads.`leads_ts` AS 'DATE PROCESSED'
FROM `bcrm`.`leads`
LEFT JOIN `bcrm`.`client`
    ON (`leads`.`leads_client_id` = `client`.`client_id`)
LEFT JOIN `bcrm`.`users`
    ON (`leads`.`leads_users_id` = `users`.`users_id`)
LEFT JOIN `bcrm`.`leads_substatus` 
    ON (`leads`.`leads_substatus_id` = `leads_substatus`.`leads_substatus_id`)
LEFT JOIN `bcrm`.`leads_status`
    ON (`leads`.`leads_status_id` = `leads_status`.`leads_status_id`)
LEFT JOIN bcrm.dynamic_value AS dv1 
    ON (dv1.dynamic_value_lead_id = leads.leads_id AND dv1.dynamic_value_dynamic_id = 2768)
LEFT JOIN bcrm.dynamic_value AS dv2 
    ON (dv2.dynamic_value_lead_id = leads.leads_id AND dv2.dynamic_value_dynamic_id = 2769)
LEFT JOIN bcrm.dynamic_value AS dv3 
    ON (dv3.dynamic_value_lead_id = leads.leads_id AND dv3.dynamic_value_dynamic_id = 2770)
LEFT JOIN bcrm.dynamic_value AS dv4 
    ON (dv4.dynamic_value_lead_id = leads.leads_id AND dv4.dynamic_value_dynamic_id = 4050)
LEFT JOIN bcrm.dynamic_value AS dv5 
    ON (dv5.dynamic_value_lead_id = leads.leads_id AND dv5.dynamic_value_dynamic_id = 2777)
LEFT JOIN bcrm.dynamic_value AS dv6
    ON (dv6.dynamic_value_lead_id = leads.leads_id AND dv6.dynamic_value_dynamic_id = 2778)
LEFT JOIN `bcrm`.`dynamic_value` AS dv7 
    ON dv7.`dynamic_value_lead_id` = `leads`.`leads_id` 
    AND dv7.`dynamic_value_dynamic_id` = 5872
WHERE  client.`client_name` = 'PIF LEGAL'
AND leads.`leads_users_id` <> 659;