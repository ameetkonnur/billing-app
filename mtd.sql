# define view "current_month_trend"
CREATE VIEW `current_month_trend` AS 
(select sum(`azure_usage`.`Cost`) AS `sum(cost)`,`azure_usage`.`subscriptionName` AS `subscriptionname`,`azure_usage`.`meterSubCategory` AS `meterSubCategory`,`azure_usage`.`billing_date` AS `billing_date` 
from `azure_usage` 
where 
(`azure_usage`.`billing_date` between date_format(now(),'%Y-%m-01') and now()) 
group by 
`azure_usage`.`subscriptionName`,`azure_usage`.`meterSubCategory`,`azure_usage`.`billing_date` order by `azure_usage`.`billing_date`);

# get billing details from view "current_month_trend"
select * from current_month_trend

