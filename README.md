# billing-app
This application gives an option to configure monthly limits at a resourceGroup Level and have alerts set to specific emailID's.

It uses the publicly available billing API for Azure Usage (https://docs.microsoft.com/en-us/rest/api/billing/enterprise/billing-enterprise-api-usage-detail). 

Technology Stack : Python 3.5+, mySQL DB 5.7

Python Packages : mysql-connector

The data is pulled on a daily basis (T-2 to accomodate delay in billing reflected) & is stored in a mySQL DB.
Once stored the application checks for usage per resourceGroup against thresholds and calculates % against Limits set.
The Limits are set as a part of the configuration in a mySQL DB table.

Application Components
  
  getusage.py : Gets usage details from billing API and inserts it into mySQL DB
  
  sendmail.py : Checks against limits and sends alerts on usage against limits
  
  config.json : All config parameters including mySQL DB, SMTP & others (rename config.sample.json to config.json)
  
  schema.sql : creates mysql tables and default records
  
  Frequency : Daily configured as CRON jobs
  
  To pull in historical data update the config.json parameters as below
  
  Example if you want last 15 days data update the below parameters as shown
  
  "billing_lag":"15",  --> for 15 days historical data update this to 15.
  
  "no_of_days":"14", --> add 14 days to above date
