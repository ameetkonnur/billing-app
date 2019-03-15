#!/bin/bash
service ssh start
superset runserver -d
/usr/sbin/sshd
