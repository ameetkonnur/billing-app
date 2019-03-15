#!/bin/bash
service ssh start
/usr/sbin/sshd
superset init
superset runserver -d

