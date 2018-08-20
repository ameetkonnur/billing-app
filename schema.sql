--mysql create table
create table azure_usage (
        Cost int,
        accountId  int,
        productId int,
        resourceLocationId int,
        consumedServiceId int,
        departmentId int,
        accountOwnerEmail varchar(50),
        accountName varchar(50),
        serviceAdministratorId varchar(50),
        subscriptionId int,
        subscriptionGuid varchar(50),
        subscriptionName varchar(50),
        billing_date date,
        product varchar(50),
        meterId varchar(50),
        meterCategory varchar(50),
        meterSubCategory varchar(50),
        meterRegion varchar(50),
        meterName varchar(50),
        consumedQuantity int,
        resourceRate int,
        resourceLocation varchar(50),
        consumedService varchar(50),
        instanceId varchar(50),
        serviceInfo1 varchar(50),
        serviceInfo2 varchar(50),
        additionalInfo varchar(200),
        tags varchar(50),
        storeServiceIdentifier varchar(50),
        departmentName varchar(50),
        costCenter varchar(50),
        unitOfMeasure varchar(50),
        resourceGroup varchar(50)
)

-- create other config tables & default values
create table default_config (config_name varchar(100), config_value varchar(255))

insert into default_config values ('rg_default_quota', 100000)
insert into default_config values ('rg_green_quota_threshold_percentage', 70)
insert into default_config values ('rg_yellow_quota_threshold_percentage', 90)
insert into default_config values ('rg_red_quota_threshold_percentage', 100)

-- create table for rg level limits & emailID for alerts
create table rg_config (rg_name varchar(200), rg_limit int, rg_email varchar(500))

-- insert value for each rg and email ID
insert rg_config values ('Resource Group',100000,'email@email.com')

-- usage against thresholds
select azure_usage.Costs , azure_usage.rg, azure_usage.rg_limit, azure_usage.usagepercentage, email,
case 
when azure_usage.usagepercentage <= 70 then 'GREEN'
when azure_usage.usagepercentage > 70 and usagepercentage <= 90 then 'YELLOW'
when azure_usage.usagepercentage > 90 then 'RED'
end as flag
from 
(

select 
sum(u.Cost) Costs, u.resourceGroup rg, r.rg_limit rg_limit , (sum(Cost) / r.rg_limit * 100) usagepercentage, r.rg_email email
from 
azure_usage u, rg_config r
where
u.resourceGroup = r.rg_name
and month(u.billing_date) = month(sysdate())
group by 
u.resourceGroup

UNION

select 
sum(u.Cost) Costs, u.resourceGroup rg, c.config_value rg_limit , (sum(u.Cost) / c.config_value * 100) usagepercentage, 'email@email.com' email
from 
azure_usage u, default_config c, rg_config r
where 
c.config_name = 'rg_default_quota' 
and r.rg_name != u.resourceGroup
and month(u.billing_date) = month(sysdate())
group by 
u.resourceGroup
) azure_usage
order by usagepercentage desc

-- optional elements not currently used
select count(*) from azure_usage

select resourceGroup, sum(Cost) Costs from azure_usage group by resourceGroup order by Costs desc limit 10

create view top10usage as select resourceGroup, sum(Cost) Costs from azure_usage group by resourceGroup order by Costs desc limit 10

select * from top10usage

create view thismonthusage as select sum(Cost) as Costs from azure_usage

select month(billing_date), year(billing_date) from azure_usage

select count(distinct resourceGroup) from azure_usage group by subscriptionName

select subscriptionName, sum(Cost) Costs from azure_usage group by SubscriptionName order by Costs desc