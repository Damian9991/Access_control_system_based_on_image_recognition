#!/usr/bin/env python3

# -----------------------------------------------------------
# Name: Access_control_system_based_on_image_recognition
# Authors: Kamil Kryczka, Damian Osinka
# Thesis supervisor: dr hab. inz. Mikołaj Leszczuk
# Purpose: Engineering Thesis
# Created: 13-10-2018
# -----------------------------------------------------------

import sqlite3
import os

import logging
logger = logging.getLogger("database_events.log")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '').replace(' ', '') + "/database_events.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class DatabaseManager(object):
    def __init__(self):
        logger.info("connecting to Access_control_system.db")
        self.db = sqlite3.connect('Access_control_system.db')
        self.cursor = self.db.cursor()

    def create_or_drop_table(self, command):
        logger.info("creating or droping table: " + command)
        self.cursor.execute(command)
        self.db.commit()

    def insert_data(self, table_name, *args):
        command = "insert into {} values{};".format(table_name, args)
        logger.info("inserting data to db: " + command)
        self.cursor.execute(command)
        self.db.commit()

    def get_users_password_from_db(self, username):
        logger.info("Fetching user's password from users database for user {}".format(username))
        query = "SELECT password FROM users WHERE username = '{}'".format(username)
        logger.info(query)
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            if not results:
                return None
            return results
        except sqlite3.OperationalError as err:
            print(str(err))
            logger.error(str(err))
            return None

    def get_licence_plate_number_from_db(self, owner):
        logger.info("Fetching licence plate number from licence_plates database for user {}".format(owner))
        query = "SELECT licence_plate_number FROM licence_plates WHERE name = '{}'".format(owner)
        logger.info(query)
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            if not results:
                return None
            return results[0][0]
        except sqlite3.OperationalError as err:
            print(str(err))
            logger.error(str(err))
            return None

    def check_if_user_in_database(self, owner):
        logger.info("Fetching info about {} user from licence_plates_database".format(owner))
        query = "SELECT EXISTS(SELECT * FROM licence_plates where name = '{}')".format(owner)
        logger.info(query)
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            if results[0][0] == 1:
                return True
            else:
                return False
        except sqlite3.OperationalError as err:
            print(str(err))
            logger.error(str(err))
            return None

    def close_connection_to_db(self):
        logger.info("closing connection to db")
        self.db.close()

if __name__ == "__main__":
    sql_object = DatabaseManager()
    # sql_object.create_or_drop_table("CREATE TABLE users(username TEXT, password TEXT)")
    # sql_object.create_or_drop_table("CREATE TABLE licence_plates(name TEXT, licence_plate_number TEXT)")
    # sql_object.insert_data('users', 'Kamil', "12345")
    # print(sql_object.check_if_user_in_database('Kamil_Kryczka'))
    sql_object.close_connection_to_db()
