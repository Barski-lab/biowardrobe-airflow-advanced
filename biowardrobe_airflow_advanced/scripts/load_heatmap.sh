#!/bin/sh
HOME=/home/airflow
echo "/usr/bin/sudo -u airflow biowardrobe-advanced-load-heatmap --uid=$1 2>&1 1>>/tmp/RunAdvanced.log" >> /tmp/RunAdvanced.log 2>&1
/usr/bin/sudo -u airflow biowardrobe-advanced-load-heatmap --uid=$1 2>&1 1>>/tmp/RunAdvanced.log