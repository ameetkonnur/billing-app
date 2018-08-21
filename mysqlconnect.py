import mysql.connector
import json
from datetime import date, timedelta
import logging

with open('config.json','r') as file:
    config = json.load(file)

mysql_user = config['mysql_username']
mysql_password = config['mysql_password']
mysql_host = config['mysql_server_fqdn']
mysql_db = config['mysql_db']
mysql_server = config['mysql_server']

billing_api_endpoint = config['billing_api_endpoint']
billig_api_key = config['billing_api_key']
enrollment_no = config['enrollment_no']

smtp_server = config['smtp']
smtp_username = config['smtp_user_name']
smtp_password = config['smtp_password']
smtp_port = config['smtp_port']
smtp_from_address = config['email_from_address']
smtp_default_address = config['email_to_default_address']

billing_lag = config['billing_lag']

conn = mysql.connector.connect(user=mysql_user,password=mysql_password,host=mysql_host,database=mysql_db)
print (conn.is_connected)
conn.close

startTime = (date.today() - timedelta(int(billing_lag))).strftime('%Y-%m-%d')
print (startTime)

logging.basicConfig(filename='billing-log',filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%Y:%m:%d %H:%M:%S',level=logging.DEBUG)
logging.info("connected to mysql")
#self.logger = logging.getLogger('billing-log')

print (date.today().strftime('%B'))