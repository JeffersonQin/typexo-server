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
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , "SQL command: ", sql)

def db_cache():
	# Export database to cache
	conn = pymysql.connect(**conf['database'])
	data_sql = pd.read_sql("select * from typecho_contents", conn)
	data_sql.to_csv(cache_dir)

def db2dict():
	# Export database to dict
	conn = pymysql.connect(**conf['database'])
	data_sql = pd.read_sql("select * from typecho_contents", conn)
	return data_sql.to_dict()

def db_maxid():
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	sql = "SELECT MAX(cid) FROM typecho_contents"
	log_command(sql)
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		conn.close()
		return results[0][0]
	except:
		print("Error: unable to fetch data")
		conn.close()
		return -1

# dict当中字符串类型要加上单引号
def db_add(data: dict):
	# Connect to database
	conn = pymysql.connect(**conf['database'])
	cursor = conn.cursor()
	# Configure the sql command
	sql = f"INSERT INTO typecho_contents (title, slug, created, modified, text, authorId, template, type, status, password, allowComment, allowPing, allowFeed) VALUES ({data['title']}, {data['slug']}, {data['created']}, {data['modified']}, {data['text']}, {data['authorId']}, {data['template']}, {data['type']}, {data['status']}, {data['password']}, {data['allowComment']}, {data['allowPing']}, {data['allowFeed']})"
	log_command(sql)
	res = -1
	try:
		cursor.execute(sql)
		conn.commit()
		# If slug value is not specified, update it with cid
		if (data['slug'] == 'NULL'):
			sql = f"UPDATE typecho_contents SET slug={db_maxid()} WHERE cid={db_maxid()}"
			log_command(sql)
			cursor.execute(sql)
			conn.commit()
			res = db_maxid()
	except Exception as e:
		conn.rollback()
		print(repr(e))
	conn.close()
	return res

@app.get("/fetch")
def fetch(token: Optional[str] = ''):
	if (token != conf['server']['token']): return {"message": "incorrect token"}
	return db2dict()

@app.get("/push")
def push(token: Optional[str] = '', modify: Optional[list] = [], delete: Optional[list] = [], add: Optional[list] = []):
	if (token != conf['server']['token']): return {"message": "incorrect token", "code": -1}
	global flag_busy;
	if (flag_busy == True): return {"message": "another operation is in process", "code": -1}
	flag_busy = True;

	

	flag_busy = False;
	return {"todo": "todo"}

def start_server():
	uvicorn.run(app, host=conf['server']['host'], port=conf['server']['port'], debug=False)

if __name__ == '__main__':
	read_conf()
	# db_cache()
	# start_server()
	db_maxid()
	test_data = {"title": "'test title from py'", 
			"slug": "NULL", 
			"created": int(time.time()), 
			"modified": int(time.time()), 
			"text": "'工具测试内容'",
			"authorId": 1,
			"template": "NULL",
			"type": "'post'",
			"status": "'publish'",
			"password": "NULL",
			"allowComment": 1,
			"allowPing": 1,
			"allowFeed": 1
			}
	print(db_add(test_data))