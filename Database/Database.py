#!/usr/bin/env python3

import sqlite3
import os

import logging
logger = logging.getLogger("database_events.log")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '') + "/database_events.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class DatabaseManager(object):
    def __init__(self):
        logger.info("connecting to Access_control_system.db")
        self.db = sqlite3.connect('../Database/Access_control_system.db')
        self.cursor = self.db.cursor()

    def close_connection_to_db(self):
        logger.info("closing connection to db")
        self.db.close()

# ----------------------------------------- system administrators management ----------------------------------------- #

    def add_user_to_db(self, username, password_hash):
        try:
            insert_data = "INSERT INTO users(username, password) VALUES(?,?)"
            self.cursor.execute(insert_data, [username, password_hash])
            self.db.commit()
            return True
        except Exception as err:
            logger.error(str(err))

    def del_user_from_db(self, username):
        try:
            delete_data = "DELETE FROM users WHERE username=?"
            self.cursor.execute(delete_data, [username])
            self.db.commit()
            return True
        except Exception as err:
            logger.error(str(err))

    def check_if_user_in_database(self, user):
        table = "users"
        logger.info("Fetching info about {} user from {}".format(user, table))
        query = "SELECT EXISTS(SELECT * FROM ? where username = ?)"
        logger.info(query)
        try:
            self.cursor.execute(query, [table, user])
            results = self.cursor.fetchall()
            if results[0][0] == 1:
                return True
            else:
                return False
        except sqlite3.OperationalError as err:
            logger.error(str(err))
            return None

    # def get_users_password_hash_from_db(self, username):
    #     logger.info("Fetching user's password from users database for user {}".format(username))
    #     query = "SELECT password FROM users WHERE username = ?"
    #     logger.info(query)
    #     try:
    #         self.cursor.execute(query, [username])
    #         results = self.cursor.fetchall()
    #         if not results:
    #             return None
    #         return results
    #     except sqlite3.OperationalError as err:
    #         logger.error(str(err))
    #         return None

    def check_login_and_password_hash(self, table_name, login, password_hash):
        logger.info("checking data in db: " + login)
        query = "SELECT * FROM ? WHERE username = ? AND password =?"
        try:
            self.cursor.execute(query, [table_name, login, password_hash])
            results = self.cursor.fetchall()
            return results
        except sqlite3.OperationalError as err:
            logger.error(str(err))

# --------------------------------------------- system users management --------------------------------------------- #

    def add_licence_plate_and_owner_to_db(self, licence_plate_number, owner):
        try:
            command = "insert into licence_plates values(?, ?);"
            logger.info("inserting data to db: {}, {}".format(owner, licence_plate_number))
            self.cursor.execute(command, [owner, licence_plate_number])
            self.db.commit()
            return True
        except Exception as err:
            logger.error(str(err))

    def del_owner_from_database(self, owner):
        query = "DELETE FROM licence_plates WHERE owner = ?"
        logger.info("deleting data from db for user: {}".format(owner))
        try:
            self.cursor.execute(query, [owner])
            self.db.commit()
        except sqlite3.OperationalError as err:
            logger.error(str(err))

    def del_licence_plate_from_database(self, licence_plate):
        query = "DELETE FROM licence_plates WHERE licence_plate_number = ?"
        logger.info("deleting data from db for licence plate: ".format(licence_plate))
        try:
            self.cursor.execute(query, [licence_plate])
            self.db.commit()
        except sqlite3.OperationalError as err:
            logger.error(str(err))

    def fetch_licence_plates_and_owners(self):
        drivers_dict = {}
        self.cursor.execute('SELECT * from licence_plates order by licence_plate_number;')
        results = self.cursor.fetchall()
        for row in results:
            if row[0] not in drivers_dict:
                drivers_dict[row[0]] = [row[1]]
            else:
                drivers_dict[row[0]].append(row[1])
        return drivers_dict

    def check_if_owner_in_database(self, owner):
        logger.info("Fetching info about {} user from licence_plates_database".format(owner))
        query = "SELECT EXISTS(SELECT * FROM licence_plates where owner = ?)"
        logger.info(query)
        try:
            self.cursor.execute(query, [owner])
            results = self.cursor.fetchall()
            if results[0][0] == 1:
                return True
            else:
                return False
        except sqlite3.OperationalError as err:
            logger.error(str(err))

    def get_licence_plates_from_db(self, owner):
        licence_plates = []
        logger.info("Fetching licence plate number from licence_plates database for user {}".format(owner))
        query = "SELECT licence_plate_number FROM licence_plates WHERE owner = ?"
        try:
            self.cursor.execute(query, [owner])
            results = self.cursor.fetchall()
            for item in results:
                licence_plates.append(item[0])
            logger.info(licence_plates)
            return licence_plates
        except sqlite3.OperationalError as err:
            logger.error(str(err))
            return None
