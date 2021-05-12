For English README, please visit [here](README-en.md).

**本项目仍在开发之中，不建议现在使用。**

# 介绍

受到`Hexo`这样的基于`node`的，可以本地编辑博客的启发，`typexo`旨在对于`typecho`的博客开发类似的功能。本项目`typexo-server`是服务器端的实现，用于接收数据，更新数据库。

目前本项目针对`MySQL`数据库的博客开发，其他数据库日后会进行支持。

**请注意：本程序会直接对数据库进行操作，如果你不知道程序在干什么，请勿执行。硬盘有价，数据无价。请确保在操作之前对数据库进行备份。**

# 环境

- Python 3.7+
- MySQL

# API文档

中文API文档：[Click](API.md).
English API Document: [Click](API-en.md)

# 使用方法

1. 新建`config.yml`。将`config_template.yml`复制一份，并重命名为`config.yml`。
2. 配置`config.yml`，下面为各个字段的含义：
    - database: 数据库字段
        - host: 数据库的host
        - user: 用于连接数据库的用户名
        - passwd: 登录数据库的密码
        - port: 数据库端口，默认为3306
        - db: `typecho`数据库的名称，一般为`typecho`
        - charset: 默认情况下，`typecho`的字符集为`utf8`，如果开起了表情支持等其他功能，可能为`utf8mb4`，具体请自己查看
    - server: 服务器字段
        - host: 服务器程序的host，如果开启了本地代理，请使用`127.0.0.1`，反之，可以使用`0.0.0.0`允许一切连接
        - port: 服务器程序端口
        - token: 用于验证请求
3. 运行脚本：
   ```bash
   python3 main.py
   ```
   后台运行：
   ```bash
   nohup python3 main.py >> log.out &
   ```
