import yaml
import pymysql
import os
import pandas as pd
import sys
import uvicorn
import requests
from fastapi import FastAPI
from typing import Optional
import time

# Initialization for paths & caches
root_dir = os.path.split(os.path.abspath(__file__))[0]
config_dir = os.path.join(root_dir, 'config.yml')
conf = {}
cache_dir = os.path.join(root_dir, 'cache/export.csv')
# Initialization for server
app = FastAPI()
# Flag meaning whether another operation is in process
flag_busy = False


def read_conf():
	# Read configuration
	with open(config_dir, 'r') as f:
		contents = f.read()
		global conf
		conf = yaml.load(contents, Loader=yaml.FullLoader)


def log_command(sql: str):
	print(time.strftime("%Y-%m-%d %H:%M:%S",
		  time.localtime()), "SQL command: ", sql)


def db_cache():
	# Export database to cache
	conn = pymysql.connect(**conf['database'])
	data_sql = pd.read_sql("select * from typecho_contents", conn)
	data_sql.to_csv(cache_dir)

def db_fetch_database(db_name: str):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: FETCH", db_name)
	# Export database to dict
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
	sql = f"select * from {db_name}"
	log_command(sql)
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		conn.close()
		return {
			"code": 1,
			"message": "succeed",
			"data": results
		}
	except Exception as e:
		print(repr(e))
		conn.close()
		return {
			"code": -1,
			"message": repr(e)
		}


def db_max_cid(db_name: str):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: MAXID", db_name)
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	sql = f"SELECT MAX(cid) FROM {db_name}"
	log_command(sql)
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		conn.close()
		return results[0][0]
	except Exception as e:
		print(repr(e))
		conn.close()
		return -1


def db_max_mid(db_name: str):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: MAXID", db_name)
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	sql = f"SELECT MAX(mid) FROM {db_name}"
	log_command(sql)
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		conn.close()
		return results[0][0]
	except Exception as e:
		print(repr(e))
		conn.close()
		return -1

# dict当中字符串类型要加上单引号


def db_add_content(data: dict):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: ADD content")
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	# Configure the sql command
	sql = f"INSERT INTO typecho_contents (title, slug, created, modified, text, authorId, template, type, status, password, allowComment, allowPing, allowFeed) VALUES ({data['title']}, {data['slug']}, {data['created']}, {data['modified']}, {data['text']}, {data['authorId']}, {data['template']}, {data['type']}, {data['status']}, {data['password']}, {data['allowComment']}, {data['allowPing']}, {data['allowFeed']})"
	log_command(sql)
	res = {"code": 0, "message": ""}
	try:
		cursor.execute(sql)
		conn.commit()
		# If slug value is not specified, update it with cid
		if (data['slug'] == 'NULL'):
			sql = f"UPDATE typecho_contents SET slug = {db_max_cid('typecho_contents')} WHERE cid = {db_max_cid('typecho_contents')}"
			log_command(sql)
			cursor.execute(sql)
			conn.commit()
		res = {"code": 1, "message": "succeed", "cid": db_max_cid('typecho_contents'), "hash": data['hash']}
	except Exception as e:
		conn.rollback()
		res = {"code": -1, "message": repr(e), "cid": -1, "hash": data['hash']}
		print(repr(e))
	conn.close()
	return res


def db_delete_content(cid: int):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: DELETE content")
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	# Configure the sql command
	sql = f"DELETE FROM typecho_contents WHERE cid = {cid}"
	log_command(sql)
	res = {"code": 0, "message": ""}
	try:
		cursor.execute(sql)
		conn.commit()
		res = {"code": 1, "message": "succeed", "cid": cid}
	except Exception as e:
		conn.rollback()
		res = {"code": -1, "message": repr(e), "cid": cid}
		print(repr(e))
	conn.close()
	return res


def db_update_content(cid: int, data: dict):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: UPDATE content")
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	keys = data.keys()
	try:
		# Update with each attribute
		for key in keys:
			sql = f"UPDATE typecho_contents SET {key} = {data[key]} WHERE cid = {cid}"
			log_command(sql)
			cursor.execute(sql)
			conn.commit()
		return {"code": 1, "message": "succeed", "cid": cid}
	except Exception as e:
		conn.rollback()
		conn.close()
		print(repr(e))
		return {"code": -1, "message": repr(e), "cid": cid}


def db_add_meta(data: dict):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: ADD meta")
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	if data['slug'] == '': data['slug'] = data['name']
	# Configure the sql command
	sql = f"INSERT INTO typecho_metas (name, slug, type, description, count) VALUES ({data['name']}, {data['slug']}, {data['type']}, {data['description']}, {data['count']})"
	log_command(sql)
	res = {"code": 0, "message": ""}
	try:
		cursor.execute(sql)
		conn.commit()
		res = {"code": 1, "message": "succeed", "mid": db_max_mid("typecho_metas"), "hash": data['hash']}
	except Exception as e:
		conn.rollback()
		res = {"code": -1, "message": repr(e), "mid": -1, "hash": data['hash']}
		print(repr(e))
	conn.close()
	return res


def db_delete_meta(mid: int):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: DELETE meta")
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	# Configure the sql command
	sql = f"DELETE FROM typecho_metas WHERE mid = {mid}"
	log_command(sql)
	res = {"code": 0, "message": ""}
	try:
		cursor.execute(sql)
		conn.commit()
		res = {"code": 1, "message": "succeed", "mid": mid}
	except Exception as e:
		conn.rollback()
		res = {"code": -1, "message": repr(e), "mid": mid}
		print(repr(e))
	conn.close()
	return res


def db_update_meta(mid: int, data: dict):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: UPDATE meta")
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	keys = data.keys()
	try:
		# Update with each attribute
		for key in keys:
			sql = f"UPDATE typecho_metas SET {key} = {data[key]} WHERE mid = {mid}"
			log_command(sql)
			cursor.execute(sql)
			conn.commit()
		return {"code": 1, "message": "succeed", "mid": mid}
	except Exception as e:
		conn.rollback()
		conn.close()
		print(repr(e))
		return {"code": -1, "message": repr(e), "mid": mid}


def db_add_relationship(cid: int, mid: int):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: ADD relationship")
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	# Configure the sql command
	sql = f"INSERT INTO typecho_relationships (cid, mid) VALUES ({cid}, {mid})"
	log_command(sql)
	res = {"code": 0, "message": ""}
	try:
		cursor.execute(sql)
		conn.commit()
		res = {"code": 1, "message": "succeed", "cid": cid, "mid": mid}
	except Exception as e:
		conn.rollback()
		res = {"code": -1, "message": repr(e), "cid": cid, "mid": mid}
		print(repr(e))
	conn.close()
	return res


def db_delete_relationship(cid: int, mid: int):
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Operation: DELETE relationship")
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	# Configure the sql command
	sql = f"DELETE FROM typecho_relationships WHERE cid = {cid} AND mid = {mid}"
	log_command(sql)
	res = {"code": 0, "message": ""}
	try:
		cursor.execute(sql)
		conn.commit()
		res = {"code": 1, "message": "succeed", "cid": cid, "mid": mid}
	except Exception as e:
		conn.rollback()
		res = {"code": -1, "message": repr(e), "cid": cid, "mid": mid}
		print(repr(e))
	conn.close()
	return res


def db_add_fields(cid: int, data: dict):
	pass


def db_update_fields(cid: int, data: dict):
	pass


def db_delete_fields(cid: int, data: dict):
	pass


@app.get("/welcome")
def welcome(token: Optional[str] = ''):
	if (token != conf['server']['token']):
		return {"code": -1, "message": "incorrect token"}
	return {"code": 1, "message": "hello world"}


@app.get("/fetch")
def fetch(db: str, token: Optional[str] = ''):
	if (token != conf['server']['token']):
		return {"code": -1, "message": "incorrect token"}
	return db_fetch_database(f"{conf['database']['prefix']}{db}")


@app.get("/push_contents")
def push_contents(token: Optional[str] = '', add: Optional[list] = [], update: Optional[list] = [], delete: Optional[list] = []):
	if (token != conf['server']['token']):
		return {"code": -1, "message": "incorrect token"}
	global flag_busy
	if (flag_busy == True):
		return {"message": "another operation is in process", "code": -1}
	flag_busy = True
	res = {'code': 1, 'message': 'token correct', 'add': [], 'update': [], 'delete': []}
	# Add
	for add_item in add:
		res['add'].append(db_add_content(add_item))
	# Update
	for update_item in update:
		res['update'].append(
			db_update_content(update_item['cid'], update_item['data']))
	# Delete
	for del_item in delete:
		res['delete'].append(db_delete_content(del_item))
	flag_busy = False
	return res


@app.get("/push_metas")
def push_metas(token: Optional[str] = '', add: Optional[list] = [], update: Optional[list] = [], delete: Optional[list] = []):
	if (token != conf['server']['token']):
		return {"code": -1, "message": "incorrect token"}
	global flag_busy
	if (flag_busy == True):
		return {"message": "another operation is in process", "code": -1}
	res = {'code': 1, 'message': 'token correct', 'add': [], 'update': [], 'delete': []}
	# Add
	for add_item in add:
		res['add'].append(db_add_meta(add_item))
	# Update
	for update_item in update:
		res['update'].append(db_update_meta(update_item['mid'], update_item['data']))
	# Delete
	for del_item in delete:
		res['delete'].append(db_delete_meta(del_item))
	flag_busy = False
	return res


@app.get("/push_relationships")
def push_relationships(token: Optional[str] = '', add: Optional[list] = [], delete: Optional[list] = []):
	if (token != conf['server']['token']):
		return {"code": -1, "message": "incorrect token"}
	global flag_busy
	if (flag_busy == True):
		return {"message": "another operation is in process", "code": -1}
	res = {'code': 1, 'message': 'token correct', 'add': [], 'delete': []}
	# Add
	for add_item in add:
		res['add'].append(db_add_relationship(add_item['cid'], add_item['mid']))
	# Delete
	for del_item in delete:
		res['delete'].append(db_delete_relationship(del_item['cid'], del_item['mid']))
	flag_busy = False
	return res


def start_server():
	uvicorn.run(app, host=conf['server']['host'],
				port=conf['server']['port'], debug=False)


if __name__ == '__main__':
	read_conf()
	start_server()
