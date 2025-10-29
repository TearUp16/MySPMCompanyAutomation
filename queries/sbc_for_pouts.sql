SELECT
leads.`leads_chcode` AS 'CH CODE',
leads.`leads_acctno` AS 'PN NUMBER',
leads_user.`users_username` AS 'AGENT TAG',
leads.`leads_chname` AS 'NAME',
leads.`leads_email` AS 'EMAIL',
leads.`leads_phone` AS 'CONTACT NUMBER',
leads.`leads_ob` AS 'OUTSTANDING BALANCE',
leads.`leads_prin` AS 'ENDORSE OB',
leads.`leads_full_address` AS 'ADDRESS',
leads.`leads_full_saddress` AS 'SECONDARY',
DATE_FORMAT(leads.`leads_endo_date`, '%m/%d/%Y') AS 'ENDO DATE',
DATE_FORMAT(leads.`leads_pullout`, '%m/%d/%Y') AS 'PULL OUT DATE',
  dv1.`dynamic_value_name` AS 'DPD',
DATE_FORMAT(leads.`leads_ts`, '%m/%d/%Y %h:%i %p') AS DateProcessed,

CASE 
    WHEN DATEDIFF(CURRENT_DATE(), leads.`leads_endo_date`) >= 16 THEN 'FOR PULL OUT'
    ELSE DATEDIFF(CURRENT_DATE(), leads.`leads_endo_date`)
END AS `Days Activ`

FROM `bcrm`.`leads`
LEFT JOIN bcrm.dynamic_value AS dv1 ON (dv1.dynamic_value_lead_id = leads.leads_id AND dv1.dynamic_value_dynamic_id = 4902)
LEFT JOIN bcrm.`users` AS leads_user ON leads_user.`users_id` = leads.`leads_users_id`

WHERE leads.leads_client_id = 193
AND leads.`leads_users_id` <> 659
ORDER BY
    leads.`leads_endo_date` ASC;