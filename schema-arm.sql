create table vm_inventory
(
    resourceId text,
    vmName varchar(50),
    resourceGroup varchar(50),
    resourceLocation varchar(50),
    licenseType varchar(50),
    offer varchar(50),
    sku varchar(50),
    osType varchar(50),
    subscriptionId varchar(50),
    vmSize varchar(50),
    activeFlag int,
    updateDate date
)

create table vm_disks
(
    resourceId text,
    diskName varchar(50),
    resourceGroup varchar(50),
    resourceLocation varchar(50),
    managedBy text,
    diskSizeGB varchar(50),
    osType varchar(50),
    skuName varchar(20),
    skuTier varchar(20),
    subscriptionId varchar(50),
    activeFlag int,
    updateDate date
)


create table storage_accounts
(
    resourceId text,
    kind varchar(20),
    resourceLocation varchar(50),
    accountName varchar(50),
    resourceGroup varchar(50),
    managedBy text,
    skuName varchar(20),
    skuTier varchar(20),
    subscriptionId varchar(50),
    activeFlag int,
    updateDate date
)

create table vm_sizes
(
    maxDisks int,
    maxMemoryMb int,
    vmSize text,
    cores int,
    osDiskSizeMb int,
    resourceDiskSizeMb int
)

create view view_vmInventory as (select a.*, b.cores, b.maxMemoryMb, c.countrycode from vm_inventory a, vm_sizes b, billingdb.`dc-country` c where a.vmSize = b.vmSize and a.activeFlag = 1 and a.resourceLocation = c.dclocation)

create view view_vmDisks as (select a.* from vm_disks a where a.activeFlag = 1)

drop table vm_inventory
drop table vm_disks

drop table vm_sizes

drop view view_vmInventory
drop view view_vmDisks