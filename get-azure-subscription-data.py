import requests
import json
import mysql.connector
from datetime import date, timedelta
import logging

# set logging config
logging.basicConfig(filename='azure-billing-log',filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%Y:%m:%d %H:%M:%S',level=logging.DEBUG)
logging.info("running get_subscription_data program")
logging.info("loaded log config")

# get all config settings
with open('config.json','r') as file:
    config = json.load(file)

logging.info("loaded app config")

client_secret = config['client_secret']
tenant_id = config['tenant_id']
client_id = config['client_id']
subscription_id = config['include_subscription_id']

# AAD Token Endpoint
aad_token_endpoint = 'https://login.microsoftonline.com/{0}/oauth2/token'.format(tenant_id)

headers = {'Content-type' : 'application/x-www-form-urlencoded'}
data = {'grant_type' : 'client_credentials', 'client_id': client_id, 'client_secret' : client_secret, 'resource' : 'https://management.azure.com/'}

response = requests.post(aad_token_endpoint,headers=headers,data=data)
output = response.text

#print (output)

bearer_token = ''

if (response.status_code == 200):
    logging.info("got AAD token")
    http_response = json.loads(output)
    bearer_token = http_response['access_token']

    #API Reference : https://docs.microsoft.com/en-us/rest/api/azure/
    #arm_api_endpoint = 'https://management.azure.com/subscriptions/{0}/resourcegroups?api-version=2017-05-10'.format(subscription_id) ## List All Resource Groups
    #arm_api_endpoint = 'https://management.azure.com/subscriptions/{0}/providers/Microsoft.Advisor/recommendations?api-version=2017-03-31'.format(subscription_id) ## List Azure Advisor Recommendations
    #arm_api_endpoint = 'https://management.azure.com/subscriptions/{0}/providers/Microsoft.Compute/virtualMachines?api-version=2018-06-01'.format(subscription_id) ## List All VM's
    arm_api_endpoint = 'https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2018-09-01-preview' ##Azure Resource Graph

    '''
    headers = {'Authorization' : 'Bearer ' + bearer_token}
    response = requests.get(arm_api_endpoint,headers=headers)
    '''

    # mysql settings
    mysql_user = config['mysql_username']
    mysql_password = config['mysql_password']
    mysql_host = config['mysql_server_fqdn']
    mysql_db = config['mysql_db']
    mysql_server = config['mysql_server']

    # open mysql connection
    conn = mysql.connector.connect(user=mysql_user,password=mysql_password,host=mysql_host,database=mysql_db)
    cursor = conn.cursor()

    ################ for VM's

    # update existing records to inActive
    cursor.execute('update vm_inventory set activeFlag = 0 where activeFlag = 1')

    headers = {'Authorization' : 'Bearer ' + bearer_token,'Content-Type':'application/json'}
    #body='{"subscriptions":["'+ subscription_id + '"],"query":"project name, type | limit 10"}'
    resource = 'Microsoft.Compute/virtualMachines'
    body='{"subscriptions":["'+ subscription_id + '"],"query":"project id, name, type, resourceGroup, location, properties.licenseType, properties.storageProfile.imageReference.offer, properties.storageProfile.imageReference.sku,properties.storageProfile.osDisk.osType, subscriptionId, properties.hardwareProfile.vmSize | where type=~ \'' + resource + '\'"}'
    response = requests.post(arm_api_endpoint,headers=headers,data=body)

    #print(response)
    resource_list = json.loads(response.text)
    #print(resource_list)

    for item in resource_list['data']['rows']:
        #print (item['properties']['vmId'])
        #print (item)
        insert_query = ('insert into vm_inventory values ("' + item[0] + '","' + item[2] + '","' + item[3] + '","' + item[4] + '","' + item[5] + '","' + item[6] + '","' + str(item[7]) + '","' + item[8] + '","' + item[9] + '","' + item[10] + '",1,"' + str(date.today()) + '")')
        print(insert_query)
        cursor.execute(insert_query)


    ################ for VM's Disks

    # update existing records to inActive
    cursor.execute('update vm_disks set activeFlag = 0 where activeFlag = 1')

    headers = {'Authorization' : 'Bearer ' + bearer_token,'Content-Type':'application/json'}
    #body='{"subscriptions":["'+ subscription_id + '"],"query":"project name, type | limit 10"}'
    resource = 'Microsoft.Compute/disks'
    body='{"subscriptions":["'+ subscription_id + '"],"query":"project type,id,name,resourceGroup,location,managedBy,properties.diskSizeGB,properties.osType,sku.name,sku.tier,subscriptionId | where type=~ \'' + resource + '\'"}'
    response = requests.post(arm_api_endpoint,headers=headers,data=body)

    print(response)
    resource_list = json.loads(response.text)
    #print(resource_list)

    for item in resource_list['data']['rows']:
        #print (item['properties']['vmId'])
        #print (item)
        insert_query = ('insert into vm_disks values ("' + item[1] + '","' + item[2] + '","' + item[3] + '","' + item[4] + '","' + item[5] + '",' + str(item[6]) + ',"' + str(item[7]) + '","' + item[8] + '","' + item[9] + '","' + item[10] + '",1,"' + str(date.today()) + '")')
        print(insert_query)
        cursor.execute(insert_query)

    '''
    ################ For Storage Accounts
    # for Storage Accounts az graph query -q "project id, kind, location, name, resourceGroup, managedBy, sku.name, sku.tier, subscriptionId, type | where type=~ 'Microsoft.Storage/storageaccounts'"

    # update existing records to inActive
    cursor.execute('update storage_accounts set activeFlag = 0 where activeFlag = 1')

    headers = {'Authorization' : 'Bearer ' + bearer_token,'Content-Type':'application/json'}
    #body='{"subscriptions":["'+ subscription_id + '"],"query":"project name, type | limit 10"}'
    resource = 'Microsoft.Storage/storageaccounts'
    body='{"subscriptions":["'+ subscription_id + '"],"query":"project id, kind, location, name, resourceGroup, managedBy, sku.name, sku.tier, subscriptionId, type | where type=~ \'' + resource + '\'"}'
    response = requests.post(arm_api_endpoint,headers=headers,data=body)

    print(response)
    resource_list = json.loads(response.text)
    #print(resource_list)

    for item in resource_list['data']['rows']:
        #print (item['properties']['vmId'])
        #print (item)
        insert_query = ('insert into storage_accounts values ("' + item[1] + '","' + item[2] + '","' + item[3] + '","' + item[4] + '","' + item[5] + '",' + str(item[6]) + ',"' + str(item[7]) + '","' + item[8] + '","' + item[9] + '","' + item[10] + '",1,"' + str(date.today()) + '")')
        print(insert_query)
        cursor.execute(insert_query)
    '''

    conn.commit()
    cursor.close()
    conn.close()

