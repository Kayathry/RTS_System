import os
from db_connector import DBConnector
from pathlib import Path
# from gsm_serial import serial_com

DB_PATH = './user/database/'


def safe_exit(signum, frame):
	exit(1)

def create_img_dir(name):
	if not os.path.exists(name):
		os.makedirs(name)

def get_next_image_path():

	p = Path(DB_PATH)
	dirs = [x for x in p.iterdir() if x.is_dir()]
	next_id = 0

	if len(dirs) == 0:
		next_id += 1
	else:
		dirs_num = [int(str(dir).split("/")[-1]) for dir in dirs]
		dirs_num.sort()
		next_id = dirs_num[-1] + 1
	
	next_path = f"{DB_PATH}/{next_id}"
	create_img_dir(next_path)

	return (next_id, next_path)

def get_next_user_id(id_name_dict):

	ids = list(id_name_dict.keys())
	next_id = int(ids[-1]) + 1
	
	next_path = os.path.join(DB_PATH,str(next_id))
	create_img_dir(next_path)

	return (next_id, next_path)

def get_img_id_path(id_name_dict):
	id_tup = get_next_user_id(id_name_dict)
	user_tup = get_next_image_path()
	img_tup = id_tup if id_tup[0] > user_tup[0] else user_tup
	return img_tup

def get_existing_user_path(id_name_dict, name):
	user_id = list(id_name_dict.keys())[list(id_name_dict.values()).index(name)]
	return os.path.join(DB_PATH,str(user_id))

		
def get_all_passwords():
	db_con = DBConnector()
	cred_dict = db_con.get_all_user_credentials()
	id_pwd, id_name = {}, {}
	for k,v in cred_dict.items():
		id_name[k] = v[0]
		id_pwd[k] = v[1]
	
	return id_pwd, id_name

# def send_alert(data):
# 	msg = f"{data[0]} entry detected at {data[1]}"
# 	serial_com(msg)

# if __name__ == '__main__':
# 	print(get_all_passwords())