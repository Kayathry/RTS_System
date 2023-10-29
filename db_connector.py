# import mysql.connector as connector
import mariadb
import datetime as dt

class DBConnector:

    def __init__(self) -> None:
        self.conn = None
        self.cursor = self.connect_db()
    
    def connect_db(self):
        try:
            self.conn = mariadb.connect(
                user="root",
                password="root",
                host="127.0.0.1",
                database="rts_db")
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            exit(-1)

        
        print("Connected to database!")
        return self.conn.cursor()

    def get_all_user_credentials(self):
        try:
            self.cursor.execute("SELECT * FROM credentials")
        except mariadb.Error as e:
            print(f"Error: {e}")

        creds_dict = {}
        for tup in self.cursor:
            creds_dict[tup[0]] = [tup[1], tup[2]]

        return creds_dict

    def insert_detection_details(self, data):
        
        try:
            self.cursor.execute("INSERT INTO image_recog_details (recognized_at, image_url, name, recognized_as) VALUES (?,?,?,?)", 
                                    (data[0],data[1], data[2], data[3]))
            print(f"Data inserted!")
            self.conn.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
        
    
    def insert_verification_details(self, data):
        
        try:
            self.cursor.execute("INSERT INTO verification_details (user_id, verified_at, is_verified) VALUES (?,?,?)",(data[0], data[1], data[2]))
            print(f"Data inserted!")
            self.conn.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")

    def close_connection(self):
        self.cursor.close()


# if __name__=='__main__':
#     db_con = DBConnector()
    # db_con.get_all_user_credentials()
    # data= [
    #     (1, dt.datetime.now(), 'user/database/1', 'Widenius', 'Widenius'),
    #     (2, dt.datetime.now(),'user/database/2', 'Widenius', 'Widenius'),
    #     (3, dt.datetime.now(),'user/database/3', 'Widenius', 'Widenius')
    # ]
    # db_con.insert_detection_details(data=data)

