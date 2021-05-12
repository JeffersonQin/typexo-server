**!!! The project is still developing. It is not recommended to use it in the present stage !!!**

# Introduction

Inspired by `node`-based blogs such as `Hexo`, which can be edited locally, this project, `typexo`, aim to implement such feature for `typecho`. `typexo-server` is the implementation of the program on server, used to receive data and update the database.

This project only support blogs using `MySQL` as database in current stage. Other types of databses would be supported in the neat future.

**Note: This program will directly manipulate the database. If you don't know what the program is doing, please do not run the script. Data is priceless, make sure to backup the database before any operations.**

# Environment

- Python 3.7+
- MySQL

# Usage

1. Create `config.yml`. Copy `config_template.yml` as `config.yml`.
2. Configurate `config.yml`. Following are the meanings of each field:
    - database:
        - host: host of database
        - user: user of database to connect
        - passwd: password of database to connect
        - port: port of database, 3306 in default
        - db: name of the database of `typecho`, `typecho` in default
        - charset: `utf8` in default. If your blog has enabled features like emoji, this field might be `utf8mb4`
    - server:
        - host: host of server, if local delegate is enabled, `127.0.0.1` is suggested. Otherwise, `0.0.0.0` can be used to allow all connections.
        - port: port of server
        - token: used to authenticate requests
3. Run script:
   ```bash
   python3 main.py
   ```
   Run in background:
   ```bash
   nohup python3 main.py >> log.out &
   ```