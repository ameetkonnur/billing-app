#!/bin/bash
crontab -l > mycron
echo "00 02 * * * python /my-app-code/billing-app/getusage.py && python /my-app-code/billing-app/get-azure-subscription-data.py && python /my-app-code/billing-app/sendmail.py" >> mycron
crontab mycron
rm mycron
service ssh start
/usr/sbin/sshd
superset init
superset runserver -d


