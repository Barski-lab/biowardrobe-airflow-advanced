#!/bin/sh
HOME=/home/airflow
echo "/usr/bin/sudo -u airflow /usr/local/bin/airflow trigger_dag --conf \"{\\\"data_uid\\\":\\\"$1\\\", \\\"intervals_uid\\\":\\\"$2\\\", \\\"name\\\":\\\"$3\\\", \\\"uid\\\":\\\"$4\\\"}\" heatmap >/tmp/RunAdvanced.log 2>&1" >> /tmp/RunAdvanced.log 2>&1
/usr/bin/sudo -u airflow /usr/local/bin/airflow trigger_dag --conf "{\"data_uid\":\"$1\", \"intervals_uid\":\"$2\", \"name\":\"$3\", \"uid\":\"$4\"}" heatmap >> /tmp/RunAdvanced.log 2>&1