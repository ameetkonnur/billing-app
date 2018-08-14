# release v1
import requests
import json
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
import mysql.connector
from datetime import date, timedelta

# get all config settings
with open('config.json','r') as file:
    config = json.load(file)

# mysql settings
mysql_user = config['mysql_username']
mysql_password = config['mysql_password']
mysql_host = config['mysql_server_fqdn']
mysql_db = config['mysql_db']
mysql_server = config['mysql_server']

# azure billing api settings
billing_api_endpoint = config['billing_api_endpoint']
billig_api_key = config['billing_api_key']
enrollment_no = config['enrollment_no']

# notification email smtp settings
smtp_server = config['smtp']
smtp_username = config['smtp_user_name']
smtp_password = config['smtp_password']
smtp_port = config['smtp_port']
smtp_from_address = config['email_from_address']
smtp_default_address = config['email_to_default_address']

# billing pull delay and no of days data to be pulled
billing_lag = config['billing_lag']
no_of_days = config['no_of_days']

# open mysql connection
conn = mysql.connector.connect(user=mysql_user,password=mysql_password,host=mysql_host,database=mysql_db)
cursor = conn.cursor()

# insert usage data query
insert_query = ("insert into azure_usage values (%(cost)s,%(accountId)s,%(productId)s,%(resourceLocationId)s,%(consumedServiceId)s,%(departmentId)s,%(accountOwnerEmail)s,%(accountName)s,%(serviceAdministratorId)s,%(subscriptionId)s,%(subscriptionGuid)s,%(subscriptionName)s,%(date)s,%(product)s,%(meterId)s,%(meterCategory)s,%(meterSubCategory)s,%(meterRegion)s,%(meterName)s,%(consumedQuantity)s,%(resourceRate)s,%(resourceLocation)s,%(consumedService)s,%(instanceId)s,%(serviceInfo1)s,%(serviceInfo2)s,%(additionalInfo)s,%(tags)s,%(storeServiceIdentifier)s,%(departmentName)s,%(costCenter)s,%(unitOfMeasure)s,%(resourceGroup)s)")

# no of records
record_count = 0

# function to write data to db
def writetodb(data):
    for item in data['data']:
        global record_count
        cursor.execute(insert_query,item)
        record_count = record_count + 1

# get start and end time for billing api call
startTime = date.today() - timedelta(int(billing_lag))
endTime = (startTime + timedelta(int(no_of_days))).strftime('%Y-%m-%d')
startTime = startTime.strftime('%Y-%m-%d')
print ('Starting download for ' + startTime + ' - ' + endTime)

# build end point
endpoint = billing_api_endpoint + enrollment_no + '/usagedetailsbycustomdate?startTime=' + startTime + '&endTime=' + endTime
#print (endpoint)

headers = {'Authorization':'Bearer ' + billig_api_key}
response = requests.get(endpoint,headers=headers)
output = response.text

# check if response is 200
if (response.status_code == 200):

    usage = json.loads(output)
    count = 1

    #first page write
    print ('Into Page ' + str(count))
    writetodb(usage)
    conn.commit()
    count = count + 1

    #subsequent page write
    while (usage['nextLink'] != ""):
        print ('Into Page ' + str(count))
        output = requests.get(endpoint,headers=headers).text
        usage = json.loads(output)
        writetodb(usage)
        count = count + 1
        if usage['nextLink'] is None:
            conn.commit()
            cursor.close()
            conn.close()
            break
        endpoint = usage['nextLink']
        conn.commit()

    print ('Run Date :: ' + str(date.today()) + ' for ' + startTime + 'to ' + endTime + '.' + str(record_count) + ' records inserted')
# if response not 200
else:
    print (str(response.status_code) + response.text)

