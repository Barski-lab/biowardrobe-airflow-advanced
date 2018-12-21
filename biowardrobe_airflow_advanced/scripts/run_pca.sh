#!/bin/sh
HOME=/home/airflow
echo "/usr/bin/sudo -u airflow /usr/local/bin/airflow trigger_dag --conf \"{\\\"uid\\\":\\\"$1\\\", \\\"expression\\\":\\\"${@:2}\\\"}\" pca >/tmp/RunAdvanced.log 2>&1" >> /tmp/RunAdvanced.log 2>&1
/usr/bin/sudo -u airflow /usr/local/bin/airflow trigger_dag --conf "{\"uid\":\"$1\", \"expression\":\"${@:2}\"}" pca >> /tmp/RunAdvanced.log 2>&1