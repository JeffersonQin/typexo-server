import yaml
import pymysql
import os
import pandas as pd
import sys
import uvicorn
import requests
from fastapi import FastAPI
from typing import Optional

# Initialization for paths & caches
root_dir = os.path.split(os.path.abspath(__file__))[0]
config_dir = os.path.join(root_dir, 'config.yml')
conf = {}
cache_dir = os.path.join(root_dir, 'cache/export.csv')
# Initialization for server
app = FastAPI()

def read_conf():
	# Read configuration
	with open(config_dir, 'r') as f:
		contents = f.read()
		global conf
		conf = yaml.load(contents, Loader=yaml.FullLoader)

def cache_db():
	# Export database to cache
	conn = pymysql.connect(**conf['database'])
	data_sql = pd.read_sql("select * from typecho_contents", conn)
	data_sql.to_csv(cache_dir)

def db2dict():
	# Export database to dict
	conn = pymysql.connect(**conf['database'])
	data_sql = pd.read_sql("select * from typecho_contents", conn)
	return data_sql.to_dict()

@app.get("/fetch")
def fetch(token: Optional[str] = ''):
	if (token != conf['server']['token']): return {"message": "incorrect token"}
	return db2dict()

def start_server():
	uvicorn.run(app, host=conf['server']['host'], port=conf['server']['port'], debug=False)

if __name__ == '__main__':
	read_conf()
	# cache_db()
	start_server()