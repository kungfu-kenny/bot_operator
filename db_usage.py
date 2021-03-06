import os
import sqlite3
from sqlite3.dbapi2 import Connection
import sqlite3
from telegram_manager import TelegramManager
from config import (name_db,
                    folder_config,
                    table_users,
                    table_groups,
                    table_locations,
                    table_users_groups,
                    table_users_locations)


class DataUsage:
    """
    class which is dedicated to produce the values of the 
    """
    def __init__(self) -> None:
        self.folder_current = os.getcwd()
        self.telegram_manager = TelegramManager()
        self.folder_config = os.path.join(self.folder_current, folder_config)
        self.create_folder = lambda x: os.path.exists(x) or os.mkdir(x)
        self.produce_values()

    def proceed_error(self, msg:str) -> None:
        """
        Method which is dedicated to send errors
        Input:  msg = message of the error
        Output: we printed and send to the telegram
        """
        print(msg)
        self.telegram_manager.proceed_message_values(msg)
            
    def check_db(self) -> None:
        """
        Test method for checking the database values
        """
        a = self.cursor.execute(f'SELECT * from {table_users};').fetchall()
        print(a)
        print('#################################################')
        b = self.cursor.execute(f'SELECT * from {table_groups};').fetchall()
        print(b)
        print('#################################################')
        c = self.cursor.execute(f'SELECT * from {table_users_groups};').fetchall()
        print(c)
        print('#################################################')
        
    def create_connection(self) -> None:
        """
        Method which is dedicated to produce the connection of the 
        Input:  None
        Output: we created the database
        """
        try:
            self.create_folder(self.folder_config)
            self.connection = sqlite3.connect(self.name_db, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception as e:
            msg = f'We faced problems with the connection. Reason: {e}'
            self.proceed_error(msg)

    def close_connection(self) -> None:
        """
        Method which is dedicated to close the 
        Input:  None
        Output: we closed the connection to the database
        """
        self.connection.close()

    def check_presence_locations(self, id_user:int) -> bool:
        """
        Method which is dedicated to check presence of the locations in the
        Input:  id_user = id to check values
        Output: booelan which signifies presence location for user
        """
        try:
            value_list = self.cursor.execute(f"SELECT * FROM {table_users_locations} where id_user={id_user};").fetchone()
            print(value_list)
            print('--------------------------------------')
            if value_list:
                return True
            return False
        except Exception as e:
            msg = f"We faced problems with checking the locations. Error: {e}"
            self.proceed_error(msg)
            return False

    def check_presence_groups(self, id_user:int) -> bool:
        """
        Method which is dedicated to check presence of selected group by user
        Input:  id_user = id to check values
        Output: boolean value which signifies presence groups for user
        """
        try:
            value_list = self.cursor.execute(f"SELECT * FROM {table_users_groups} where id_user={id_user};").fetchone()
            if value_list:
                return True
            return False
        except Exception as e:
            msg = f"We faced problems with checking the groups for users. Error: {e}"
            self.proceed_error(msg)
            return False

    def get_user_values(self, id_user:int) -> bool:
        """
        Method which is dedicated to check the presence of the 
        Input:  id_user = user id which is checked to this mission
        Output: we successfully checked presence the use within the bot
        """
        try:
            value_user = self.cursor.execute(f'SELECT id from {table_users} where id={id_user}').fetchone()
            if value_user:
                return True
            return False
        except Exception as e:
            msg = f'We found problems with checking values of the previous insertion, mistake: {e}'
            self.proceed_error(msg)

    def get_group_values(self, group_id:int, group_name:str) -> bool:
        """
        Method which is dedicated to check the presence of selected group or update name in other cases
        Input:  group_id = id of selected group
                group_name = name of the selected group
        Output: boolean value which shows presence of the 
        """
        try:
            value_list = self.cursor.execute(f"SELECT id, name FROM {table_groups} WHERE id={group_id};").fetchone()
            if not value_list:
                return False
            group_used_id, group_used_name = value_list
            if group_used_name != group_name:
                self.cursor.execute(f"UPDATE {table_groups} SET name={group_name} WHERE id={group_used_id};")
                self.connection.commit()
            return True
        except Exception as e:
            msg = f"We faced problems with checking of the group prensence. Mistake: {e}"
            self.proceed_error(msg)
            return False

    def get_current_id(self) -> int:
        """
        Method which is dedicated to manually return values from the database manually
        Input:  None
        Output: we successfully returned last id of the coordinate
        """
        try:
            return self.cursor.execute(f"SELECT MAX(id) FROM {table_locations};").fetchone()
        except Exception as e:
            msg = 'We faced some problems with the getting last id value'
            self.proceed_error(msg)
            return -1

    def insert_location(self, id_list:list, name_location:str, latitude:float, longitude:float) -> bool:
        """
        Method which is dedicated to insert location to the values
        Input:  id_list = list of the user values which inserted location
                name_location = name of the location which we would add
                latitude = latitude of the coordinates
                longitude = longitude of the coordinates
        Output: we successfully inserted coordinates and 
        """
        try:
            id_user, username, name_first, name_last = id_list
            if not self.get_user_values(id_user):
                self.insert_username(id_user, username, name_first, name_last)
            self.cursor.execute(f"INSERT INTO {table_locations} (name_location, latitude, longitude) VALUES (?, ?, ?);", 
                                (name_location, latitude, longitude))
            self.cursor.execute(f"INSERT INTO {table_users_locations} (id_user, id_location) VALUES (?, ?);", (id_user, self.cursor.lastrowid))
            self.connection.commit()
            return True
        except Exception as e:
            msg = f'We faced problems with the performing of the operating of the location inserting. Mistake: {e}'
            self.proceed_error(msg)
            return False

    def make_group_insertion(self, group_id:int, group_name:str) -> bool:
        """
        Method which is dedicated to make the group insertion
        Input:  group_id = id of the selected values
                group_name = name of the group
        Output: we successfully created 
        """
        try:
            self.cursor.execute(f"INSERT INTO {table_groups} (id, name) VALUES (?, ?);", (group_id, group_name))
            self.connection.commit()
            return True
        except Exception as e:
            msg = f"We faced problems with isertion of the groups. Mistake: {e}"
            self.proceed_error(msg)
            return False

    def connect_user_group(self, id_group:int, id_user:int) -> bool:
        """
        Method which is dedicated to connect uer to the group
        Input:  id_group = id of selected user
                id_user = id of the telegram user
        Output: we inserted to the foreign keys values
        """
        try:
            self.cursor.execute(f"INSERT INTO {table_users_groups} (id_user, id_group) VALUES (?, ?);", (id_user, id_group))
            self.connection.commit()
            return True
        except Exception as e:
            msg = f'We have problems with the connection between user and group. Mistake: {e}'
            self.proceed_error(msg)
            return False

    def disconnect_user_group(self, id_user, id_group) -> bool:
        try:
            self.cursor.execute(f"DELETE INTO {table_users_groups} WHERE id_user={id_user} AND id_group={id_group};")
            self.connection.commit()
            return True
        except Exception as e:
            msg = f'We have problems with the connection deletion between user and group. Mistake: {e}'
            self.proceed_error(msg)
            return False

    def check_user_group_connection(self, id_group:int, id_user:int) -> bool:
        """
        Method which is dedicated to check that user has added group to the connection
        Input:  id_group = id of the selected group
                id_user = id of the selected user
        Output: boolean value that signifies that we have successfully 
        """
        try:
            value_list = self.cursor.execute(f"SELECT * FROM {table_users_groups} WHERE id_group={id_group} AND id_user={id_user};").fetchone()
            if value_list:
                return True
            return False
        except Exception as e:
            msg = f"We have problem with getting values from the {table_users_groups}. Mistake: {e}"
            self.proceed_error(msg)
            return False

    def insert_group(self, group_id:int, group_name:str, id_user:int, username:str, name_first:str, name_last:str) -> bool:
        """
        Method which is dedicated to insert group which was inserted to the 
        Input:  group_id = id of the group which was inserted
                group_name = name of the group
                id_user = user id values
                username = username of the telegram
                name_first = first name of the telegram user
                name_last = last name of the telegram user
        Output: we successfully inserted values of the group
        """
        try:
            if not self.get_user_values(id_user):
                self.insert_username(id_user, username, name_first, name_last)
            if not self.get_group_values(group_id, group_name):
                self.make_group_insertion(group_id, group_name)
            if not self.check_user_group_connection(group_id, id_user):
                self.connect_user_group(group_id, id_user)
            self.connection.commit()
            return True
        except Exception as e:
            msg = f"We faced problem with inserting the group. Mistake: {e}"
            self.proceed_error(msg)
            return False
            
    def insert_username(self, id_user:int, username:str, name_first:str, name_last:str) -> bool:
        """
        Method which is dedicated to insert username to the 
        Input:  id_username = id of the selected user
                name_first = first name of the user
                name_last = last name of the user
                username = username of the 
        Output: we inserted username values
        """
        try:
            self.cursor.execute(f"INSERT INTO {table_users}(id, name_first, name_last, nickname) VALUES (?, ?, ?, ?);", 
                        (id_user, name_first, name_last, username))
            self.connection.commit()
            return True
        except Exception as e:
            msg = 'We faced problem with inserting values within the database'
            self.proceed_error(msg)
            return False

    def produce_values(self) -> None:
        """
        Method which is dedicated to create the database for the bot usage
        Input:  Nothing
        Output: we sucessfully created database with the tables
        """
        self.create_folder(self.folder_config)
        self.name_db = os.path.join(self.folder_config, name_db)
        if not os.path.exists(self.name_db) or not os.path.isfile(self.name_db):
            self.connection = sqlite3.connect(self.name_db, check_same_thread=False)
            self.cursor = self.connection.cursor()
            self.cursor.execute(f""" 
                CREATE TABLE IF NOT EXISTS {table_users}(
                    id INTEGER PRIMARY KEY,
                    name_first TEXT,
                    name_last TEXT,
                    nickname TEXT
                );""")
            self.cursor.execute(f""" 
                CREATE TABLE IF NOT EXISTS {table_locations}(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_location TEXT,
                    latitude TEXT,
                    longitude TEXT
                );""")
            self.cursor.execute(f""" 
                CREATE TABLE IF NOT EXISTS {table_groups}(
                    id INTEGER PRIMARY KEY,
                    name TEXT
                );""")
            self.cursor.execute(f""" 
                CREATE TABLE IF NOT EXISTS {table_users_groups}(
                    id_user INTEGER,
                    id_group INTEGER,
                    PRIMARY KEY (id_user, id_group),
                    FOREIGN KEY (id_user) REFERENCES {table_users} (id)
                        ON DELETE CASCADE 
                        ON UPDATE NO ACTION,
                    FOREIGN KEY (id_group) REFERENCES {table_groups} (id)
                        ON DELETE CASCADE 
                        ON UPDATE NO ACTION
                );""")
            self.cursor.execute(f""" 
                CREATE TABLE IF NOT EXISTS {table_users_locations}(
                    id_user INTEGER,
                    id_location INTEGER,
                    PRIMARY KEY (id_user, id_location),
                    FOREIGN KEY (id_user) REFERENCES {table_users} (id)
                        ON DELETE CASCADE 
                        ON UPDATE NO ACTION,
                    FOREIGN KEY (id_location) REFERENCES {table_locations} (id)
                        ON DELETE CASCADE 
                        ON UPDATE NO ACTION
                );""")
            self.connection.commit()
        else:
            self.create_connection()