#!/usr/bin/env python3

#-----------------------------------------------------------
# Name: Access_control_system_based_on_image_recognition
# Authors: Kamil Kryczka, Damian Osinka
# Thesis supervisor: dr hab. inz. Mikołaj Leszczuk
# Purpose: Engineering Thesis
# Created: 13-10-2018
#-----------------------------------------------------------

import sqlite3
import os

import logging
logger = logging.getLogger("sql.log")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '').replace(' ', '') + "/sql.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class SQLiteManager(object):
    def __init__(self, db_name):
		logger.info("connecting to db: " + db_name)
        self.db = sqlite3.connect(db_name)
        self.cursor = self.db.cursor()

    def create_or_drop_table(self, command):
		logger.info("creating or droping table: " + command)
        self.cursor.execute(command)
        self.db.commit()

    def insert_data(self, command):
		logger.info("inserting data to db: " + command)
        self.cursor.execute(command)

    def select_data(self, db_name, arg1, arg2):
		logger.info("checking data in db: " + arg1 + " " + arg2)
        query = "SELECT * FROM {} WHERE username = ? AND password =?".format(db_name)
        self.cursor.execute(query, [ (arg1), (arg2)])
        results = self.cursor.fetchall()
        return results

    def close_connection_to_db(self):
		logger.info("closing connection to db: " + command)
        self.db.close()


if __name__ == "__main__":
    sql_object = SQLiteManager("users.db")
    sql_object.create_or_drop_table("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    sql_object.close_connection_to_db()
