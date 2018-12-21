#!/bin/bash
HOME=/home/airflow
E_UID=$1
EXPR=${@:2}
echo "/usr/bin/sudo -u airflow /usr/local/bin/airflow trigger_dag --conf \"{\\\"uid\\\":\\\"$E_UID\\\", \\\"expression\\\":\\\"$EXPR\\\"}\" pca >/tmp/RunAdvanced.log 2>&1" >> /tmp/RunAdvanced.log 2>&1
/usr/bin/sudo -u airflow /usr/local/bin/airflow trigger_dag --conf "{\"uid\":\"$E_UID\", \"expression\":\"$EXPR\"}" pca >> /tmp/RunAdvanced.log 2>&1