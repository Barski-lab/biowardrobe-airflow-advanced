#!/bin/sh
HOME=/home/airflow
echo "/usr/bin/sudo -u airflow /usr/local/bin/airflow trigger_dag --conf \"{\\\"condition\\\":[\\\"$1\\\", \\\"$2\\\"], \\\"groupby\\\":$3, \\\"project_uid\\\":\\\"$4\\\", \\\"name\\\":\\\"$5\\\", \\\"uid\\\":\\\"$6\\\"}\" deseq-advanced >/tmp/RunAdvanced.log 2>&1" >> /tmp/RunAdvanced.log 2>&1
/usr/bin/sudo -u airflow /usr/local/bin/airflow trigger_dag --conf "{\"condition\":[\"$1\", \"$2\"], \"groupby\":$3, \"project_uid\":\"$4\", \"name\":\"$5\", \"uid\":\"$6\"}" deseq-advanced >> /tmp/RunAdvanced.log 2>&1