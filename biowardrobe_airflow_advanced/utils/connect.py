#! /usr/bin/env python3
import MySQLdb                                                 # TODO Do I need to add it into requirements in setup.py
import logging
from sqlparse import split
from contextlib import closing

from airflow import models
from airflow.hooks.mysql_hook import MySqlHook
from airflow.utils.db import merge_conn

from biowardrobe_airflow_advanced.utils.utilities import norm_path


logger = logging.getLogger(__name__)


def open_file(filename):
    """Returns list of lines from the text file. \n at the end of the lines are trimmed. Empty lines are excluded"""
    lines = []
    with open(filename, 'r') as infile:
        for line in infile:
            if line.strip():
                lines.append(line.strip())
    return lines


class Connect:

    def get_conn(self):
        pass

    def execute(self, sql, option=None):
        with closing(self.get_conn()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(sql)
                connection.commit()
                if option == 1:
                    return cursor.fetchone()
                elif option == 2:
                    return cursor.fetchall()
                else:
                    return None

    def fetchone(self, sql):
        return self.execute(sql,1)

    def fetchall(self, sql):
        return self.execute(sql,2)

    def get_settings_raw(self):
        return {row['key']: row['value'] for row in self.fetchall("SELECT * FROM settings")}

    def get_settings_data(self):
        settings = self.get_settings_raw()
        settings_data = {
            "home":     norm_path(settings['wardrobe']),
            "raw_data": norm_path("/".join((settings['wardrobe'], settings['preliminary']))),
            "anl_data": norm_path("/".join((settings['wardrobe'], settings['advanced']))),
            "indices":  norm_path("/".join((settings['wardrobe'], settings['indices']))),
            "upload":   norm_path("/".join((settings['wardrobe'], settings['upload']))),
            "bin":      norm_path("/".join((settings['wardrobe'], settings['bin']))),
            "temp":     norm_path("/".join((settings['wardrobe'], settings['temp']))),
            "experimentsdb": settings['experimentsdb'],
            "airflowdb":     settings['airflowdb'],
            "threads":       settings['maxthreads']
        }
        return settings_data

    def apply_patch(self, filename):
        logger.debug(f"Apply SQL patch: {filename}")
        with open(filename) as patch_stream:
            for sql_segment in split(patch_stream.read()):
                if sql_segment:
                    self.execute(sql_segment)


class DirectConnect(Connect):

    def __init__(self, config_file):
        self.config = [line for line in open_file(config_file) if not line.startswith("#")]

    def get_conn(self):
        conn_config = {
            "host": self.config[0],
            "user": self.config[1],
            "passwd": self.config[2],
            "db": self.config[3],
            "port": int(self.config[4]),
            "cursorclass": MySQLdb.cursors.DictCursor
        }
        conn = MySQLdb.connect(**conn_config)
        return conn


class HookConnect(Connect):

    CONNECTION_ID = "biowardrobe"

    def __init__(self, config_file = None):
        if config_file:
            self.config = [line for line in open_file(config_file) if not line.startswith("#")]
            merge_conn(
                models.Connection(
                    conn_id = self.CONNECTION_ID,
                    conn_type = 'mysql',
                    host = self.config[0],
                    login = self.config[1],
                    password = self.config[2],
                    schema = self.config[3],
                    extra = "{\"cursor\":\"dictcursor\"}"))
            self.get_conn()

    def get_conn(self):
        mysql = MySqlHook(mysql_conn_id=self.CONNECTION_ID)
        return mysql.get_conn()
