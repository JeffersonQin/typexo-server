import yaml
import pymysql
import os
import pandas as pd

# Obtain the absolute path of configuration file
root_dir = os.path.split(os.path.abspath(__file__))[0]
config_dir = os.path.join(root_dir, 'config.yml')

# Read configuration
conf = {}
with open(config_dir, 'r') as f:
	contents = f.read()
	conf = yaml.load(contents, Loader=yaml.FullLoader)

conn = pymysql.connect(**conf['database'])
data_sql = pd.read_sql("select * from typecho_contents", conn)
cache_dir = os.path.join(root_dir, 'cache/data.csv')
data_sql.to_csv(cache_dir)
