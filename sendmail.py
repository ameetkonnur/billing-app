# handled multiple email ID's
# added code for excluding subscriptions & email cosmetic changes
import smtplib
import mysql.connector
import json
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.message
import logging

# set logging config
logging.basicConfig(filename='azure-billing-log',filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%Y:%m:%d %H:%M:%S',level=logging.DEBUG)
logging.info("loaded log config")

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
sender = config['email_from_address']
recepient = config['email_to_default_address']

# billing pull delay and no of days data to be pulled
billing_lag = config['billing_lag']
no_of_days = config['no_of_days']

# load subscription exclusion
exclude_subscriptions = config['exclude-subscriptions']

logging.info("loaded app config")

# open mysql connection
conn = mysql.connector.connect(user=mysql_user,password=mysql_password,host=mysql_host,database=mysql_db)
conn._connection_timeout = 600
cursor = conn.cursor()

logging.info("connected to mysql billingdb")

# query to get usage against thresholds
query = '''
select azure_usage.Costs ,azure_usage.sn, azure_usage.rg, azure_usage.rg_limit, azure_usage.usagepercentage, emailId,
case 
when azure_usage.usagepercentage <= 70 then 'GREEN'
when azure_usage.usagepercentage > 70 and usagepercentage <= 90 then 'YELLOW'
when azure_usage.usagepercentage > 90 then 'RED'
end as flag
from 
(

select 
sum(u.Cost) Costs, u.subscriptionName sn, u.resourceGroup rg, r.rg_limit rg_limit , (sum(Cost) / r.rg_limit * 100) usagepercentage, r.rg_email emailId
from 
azure_usage u, rg_config r
where
u.resourceGroup = r.rg_name
and month(u.billing_date) = month(sysdate())
group by 
u.resourceGroup

UNION

select 
sum(u.Cost) Costs, u.subscriptionName sn, u.resourceGroup rg, c.config_value rg_limit , (sum(u.Cost) / c.config_value * 100) usagepercentage, 'default' emailId
from 
azure_usage u, default_config c
where 
u.resourceGroup not in (select rg_name from rg_config)
and c.config_name = 'rg_default_quota' 
and month(u.billing_date) = month(sysdate())
group by 
u.resourceGroup
) azure_usage
order by usagepercentage desc
'''

# execute query
cursor.execute(query)

logging.info("ran query")

# open smtp connection
smtp = smtplib.SMTP(smtp_server + ':' + smtp_port)
smtp.ehlo()
smtp.starttls()
smtp.login(smtp_username,smtp_password)

# set variable values
month = date.today().strftime('%B')
count = 0

# loop in for all results
for (Costs,sn,rg,rg_limit,usagepercentage,emailId,flag) in cursor:
    
    if sn in exclude_subscriptions:
        logging.info ('Skipped ' + rg + ' for subscription ' + sn)
    else:
        # create the email object & html message body
        message = email.message.Message()
        message.add_header('Content-Type','text/html')
        message['From'] = sender

        if emailId == 'default':
            recepient = config['email_to_default_address']
            message['To'] = recepient
        else:
            recepient = emailId
            message['To'] = recepient
        
        message['Subject'] = 'Your usage for resourceGroup {} for month {} is INR {} at is at {} % of your quota'.format(rg,month,Costs,usagepercentage)
        #text_message = 'Your usage for month {} is INR {} at is at {} % of your quota'.format(str(date.today),Costs,usagepercentage)
        html_message = '''
        <html>
            <body>
                <table>
                    <tr>
                        <td colspan='2'> Subscription Name : <b>{}</b></td>
                    </tr>
                    <tr>
                        <td bgcolor='{}'>    </td>
                        <td> Your usage for resourceGroup <b>{}</b> for the month of {} is INR <b>{}</b> at is at <b>{}</b> % of your quota. </td>
                    </tr>
                </table>
            </body>
        </html>
        '''.format(sn,flag,rg,month,Costs,usagepercentage)

        message.set_payload(html_message)
        #print (html_message)
        smtp.sendmail(sender,recepient.split(','),message.as_string())
        count = count + 1

logging.info(str(count) + " mail(s) sent")
print (str(count) + " mail(s) sent")

# close smtp connection
smtp.quit()

# close mysql connection
conn.close()
