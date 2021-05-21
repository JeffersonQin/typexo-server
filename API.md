# typecho数据库设计解释

typecho官方对于数据库的说明文档：https://docs.typecho.org/database

由于官方说明某些地方十分模棱两可，并且并没有给出详细的可选参数，这里特意做一些额外解释：

## typecho_contents

**功能**：存储文章和页面的信息

|     键名     |     类型     |       属性       |               解释                |
| :----------: | :----------: | :--------------: | :-------------------------------: |
|     cid      |   int(10)    |  主键,非负,自增  |            post表主键             |
|    title     | varchar(200) |      可为空      |             内容标题              |
|     slug     | varchar(200) |   索引,可为空    |            内容缩略名             |
|   created    |   int(10)    | 索引,非负,可为空 |    内容生成时的GMT unix时间戳     |
|   modified   |   int(10)    |   非负,可为空    |    内容更改时的GMT unix时间戳     |
|     text     |     text     |      可为空      |             内容文字              |
|    order     |   int(10)    |   非负,可为空    |               排序                |
|   authorId   |   int(10)    |   非负,可为空    |          内容所属用户id           |
|   template   | varchar(32)  |      可为空      |          内容使用的模板           |
|     type     | varchar(16)  |      可为空      |             内容类别              |
|    status    | varchar(16)  |      可为空      |             内容状态              |
|   password   | varchar(32)  |      可为空      | 受保护内容,此字段对应内容保护密码 |
| commentsNum  |   int(10)    |   非负,可为空    |      内容所属评论数,冗余字段      |
| allowComment |   char(1)    |      可为空      |           是否允许评论            |
|  allowPing   |   char(1)    |      可为空      |           是否允许ping            |
|  allowFeed   |   char(1)    |      可为空      |         允许出现在聚合中          |

- **order**: 对于文章(`post`), `order = 0`, 对于页面(`pages`), `order`从1开始计数。<br/>
  **重要: 由于直接添加order数据库会报错，所有请求中的add字段不得有order元素，即使有也不会被处理。同时，在update字段也请尽量避免对order的操作，尽可能在网站控制台进行操作。**
- **template**: 使用的模板，具体获取方式:<br/>
  ![](https://cdn.jsdelivr.net/gh/JeffersonQin/blog-asset@latest/usr/picgo/20210512183849.png)
- **type**: 内容类别, 可选值: `post`, `post_draft`, `page`, `page_draft`
- **status**: 状态
  - `post`的可选值: `publish`, `hidden`, `password`, `private`, `waiting`
  - `page`的可选值: `publish`, `hidden`
  ![](https://cdn.jsdelivr.net/gh/JeffersonQin/blog-asset@latest/usr/picgo/20210512183850.png)
- **password**: 密码，在`post`为`password`时生效
- **commentsNum**: 评论数，无需考虑

## typecho_metas

**功能**：存储`tag`和`category`的信息

|    键名     |     类型     |      属性      |           解释           |
| :---------: | :----------: | :------------: | :----------------------: |
|     mid     |   int(10)    | 主键,非负,自增 |         项目主键         |
|    name     | varchar(200) |     可为空     |           名称           |
|    slug     | varchar(200) |  索引,可为空   |        项目缩略名        |
|    type     | varchar(32)  |     可为空     |         项目类型         |
| description | varchar(200) |     可为空     |         选项描述         |
|    count    |   int(10)    |  非负,可为空   |     项目所属内容个数     |
|    order    |   int(10)    |  非负,可为空   |         项目排序         |
|   parent    |   int(10)    |  非负,可为空   | 只有`category`有, 父类别 |

- **order**: 对于文章(`post`), `order = 0`, 对于页面(`pages`), `order`从1开始计数。<br/>
  **重要: 由于直接添加order数据库会报错，所有请求中的add字段不得有order元素，即使有也不会被处理。同时，在update字段也请尽量避免对order的操作，尽可能在网站控制台进行操作。**
- **type**: 可选值, `tag`, `category`
- 对于`tag`, 默认情况下, `slug`和`name`相同, `description = null`

## typecho_relationships

**功能**：`cid`和`mid`配对, 即：文章和标签、类别配对

| 键名  |  类型   |   属性    |   解释   |
| :---: | :-----: | :-------: | :------: |
|  cid  | int(10) | 主键,非负 | 内容主键 |
|  mid  | int(10) | 主键,非负 | 项目主键 |

# typexo服务器API文档

## 重要：关于数据格式

由于在`push`中，和数据库相关的数据都是直接传给数据库的, 所以有一下约定：对于add/update/delete的数据，若为

- int类型：直接使用数字
- string类型：双引号之内还要增加一层单引号
- 其他类型 (e.g. NULL)：使用双引号括起来即可

除此之外，`string`类型若涉及转义字符，还需进行反转义。

## token

服务器所有请求都采用`token`验证, 如果不想启用`token`, 只需要在`config.yml`中的`server/token`字段留空即可。

若`token`验证失败, 会返回：

```json
{
    "code": -1,
    "message": "incorrect token"
}
```

## GET /welcome

- **功能**: 连通性测试
- **参数列表**:
    | 参数  |     说明     | 可选  |    示例    |
    | :---: | :----------: | :---: | :--------: |
    | token | 用于请求验证 |   ✅   | your_token |
- **返回值示例**:
    ```json
    {
        "code": 1,
        "message": "hello world"
    }
    ```
- **返回值说明**:
  | 返回值  |           说明            | 数据格式 |    示例     |
  | :-----: | :-----------------------: | :------: | :---------: |
  |  code   | 状态码, 1为成功, -1为失败 |   int    |      1      |
  | message |           消息            |  string  | hello world |

## GET /fetch

- **功能**: 拉取服务端数据库
- **参数列表**:
    | 参数  |     说明     | 可选  |    示例    |
    | :---: | :----------: | :---: | :--------: |
    | token | 用于请求验证 |   ✅   | your_token |
    | db | 数据库名称(除去前缀) |   ❌   | contents |
- **返回值示例**:
    ```json
    {
        "code": 1,
        "message": "succeed",
        "data": [
            {
                "cid": 1,
                "title": "文章标题",
                "slug": "1",
                "created": 1605280680,
                "modified": 1605781494,
                "text": "<!--markdown-->\r\n测试文章内容",
                "order": 0,
                "authorId": 1,
                "type": "post",
                "template": "null",
                "status": "publish",
                "password": "null",
                "commentsNum": 48,
                "allowComment": "1",
                "allowPing": "1",
                "allowFeed": "1",
                "parent": 0,
                "views": 0
            },
            {
                "cid": 2,
                "title": "页面标题",
                "slug": "page",
                "created": 1605280680,
                "modified": 1605781494,
                "text": "<!--markdown-->\r\n测试文章内容",
                "order": 1,
                "authorId": 1,
                "type": "post",
                "template": "github.pip",
                "status": "publish",
                "password": "abc",
                "commentsNum": 48,
                "allowComment": "1",
                "allowPing": "1",
                "allowFeed": "1",
                "parent": 0,
                "views": 0
            }
        ]
    }
    ```
	```json
    {
		"code": 1,
		"message": "succeed",
		"data": [
			{
				"mid": 19,
				"name": "VPS",
				"slug": "VPS",
				"type": "tag",
				"description": null,
				"count": 2,
				"order": 0,
				"parent": 0
			},
			{
				"mid": 2,
				"name": "AI",
				"slug": "AI",
				"type": "tag",
				"description": null,
				"count": 1,
				"order": 0,
				"parent": 0
			},{
				"mid": 3, 
				"name": "DL",
				"slug": "DL",
				"type": "category",
				"description": "Deep Learning",
				"count": 1,
				"order": 1,
				"parent": 0
			}
		]
	}
    ```
	```json
    {
        "code": 1,
        "message": "succeed",
        "data": [
            {
				"cid": 5,
				"mid": 3
			},
			{
				"cid": 5,
				"mid": 4
			}
        ]
    }
    ```
- **返回值说明**:
  | 返回值  |                说明                 | 数据格式 |  示例   |
  | :-----: | :---------------------------------: | :------: | :-----: |
  |  code   |      状态码, 1为成功, -1为失败      |   int    |    1    |
  | message |        消息, 成功为"succeed"        |  string  | succeed |
  |  data   | 文章数据, 请参照typecho数据库设计解释 |   list   |   略    |

## POST /push_contents

- **功能**: 更新文章和页面数据
- **参数列表**:
    | 参数  | 说明  | 可选  | 示例  |
    | :---: | :---: | :---: | :---: |
    | token | 用于请求验证 | ✅ | your_token |
    | add | 增加文章和页面, 是一个list。每个元素都有两个键值, 第一个键值为`hash`, 作为验证, 在本次增加的所有数据中应具有唯一性；第二个键值为`data`, 数据格式请参照typecho数据库设计解释 | ✅ | `[{"hash": 1323795, "data": <page_data_1>}, {"hash": 437289, "data": <page_data_2>}, ...]` |
    | update | 更改已有文章和页面, 是一个list。每个元素都有两个键值, 第二个键值为文章`cid`, 第二个键值为`data`, 数据格式请参照typecho数据库设计解释。注：这里数据不需完全, 只需包含更改的条目 | ✅ | `[{"cid": 1, "data": <page_data_1>}, {"cid": 2, "data": <page_data_2>}, ...]` |
    | delete | 删除文章和页面, 是一个list, 包含了所有需要删除内容的`cid` | ✅ | `[1, 2, 3]` |
- **返回值示例**:
    ```json
    {
        "code": 1,
        "message": "token correct",
        "add": [
            {
                "code": 1,
                "message": "succeed",
                "cid": 23,
                "hash": 546782
            },
            {
                "code": -1,
                "message": "DataError(1366, \"Incorrect string value: \\'\\\\\\\\xF0\\\\\\\\x9F\\\\\\\\x98\\\\\\\\x80\\' for column \\'text\\' at row 1\")",
                "cid": -1,
                "hash": 346252
            }
        ],
        "update": [
            {
                "code": 1,
                "message": "succeed",
                "cid": 12
            },
            {
                "code": -1,
                "message": "IntegrityError(1062, \"Duplicate entry \\'test-slug\\' for key \\'slug\\'\")",
                "cid": 13
            }
        ],
        "delete": [
            {
                "code": 1,
                "message": "succeed",
                "cid": 7
            }
        ]
    }
    ```
- **返回值说明**
  | 返回值  |           说明            | 数据格式 |     示例      |
  | :-----: | :-----------------------: | :------: | :-----------: |
  |  code   | 状态码, 1为成功, -1为失败 |   int    |       1       |
  | message |           消息            |  string  | token correct |
  |   add   |    增加文章的状态返回     |   list   |      略       |
  | update  |    文章修改的状态返回     |   list   |      略       |
  | delete  |    删除文章的状态返回     |   list   |      略       |
- **增加文章状态返回参数说明**
  | 返回值  |               说明                | 数据格式 |  示例   |
  | :-----: | :-------------------------------: | :------: | :-----: |
  |  code   |     状态码, 1为成功, -1为失败     |   int    |    1    |
  | message |    消息, 失败则返回数据库报错     |  string  | succeed |
  |   cid   | 成功后返回新文章的cid, 失败返回-1 |   int    |   234   |
  |  hash   |   同/push的参数列表中add的hash    |   int    | 346252  |
- **文章修改状态返回参数说明**
  | 返回值  |            说明            | 数据格式 |  示例   |
  | :-----: | :------------------------: | :------: | :-----: |
  |  code   | 状态码, 1为成功, -1为失败  |   int    |    1    |
  | message | 消息, 失败则返回数据库报错 |  string  | succeed |
  |   cid   |       操作文章的cid        |   int    |   234   |
- **删除文章状态返回参数说明**
  | 返回值  |            说明            | 数据格式 |  示例   |
  | :-----: | :------------------------: | :------: | :-----: |
  |  code   | 状态码, 1为成功, -1为失败  |   int    |    1    |
  | message | 消息, 失败则返回数据库报错 |  string  | succeed |
  |   cid   |       删除文章的cid        |   int    |   234   |

## POST /push_metas

- **功能**: 更新meta数据
- **参数列表**:
    | 参数  | 说明  | 可选  | 示例  |
    | :---: | :---: | :---: | :---: |
    | token | 用于请求验证 | ✅ | your_token |
    | add | 增加meta, 是一个list。每个元素都有两个键值, 第一个键值为`hash`, 作为验证, 在本次增加的所有数据中应具有唯一性；第二个键值为`data`, 数据格式请参照typecho数据库设计解释 | ✅ | `[{"hash": 1323795, "data": <meta_data_1>}, {"hash": 437289, "data": <meta_data_2>}, ...]` |
    | update | 更改已有meta, 是一个list。每个元素都有两个键值, 第二个键值为meta元素的`mid`, 第二个键值为`data`, 数据格式请参照typecho数据库设计解释。注：这里数据不需完全, 只需包含更改的条目 | ✅ | `[{"mid": 1, "data": <meta_data_1>}, {"mid": 2, "data": <meta_data_2>}, ...]` |
    | delete | 删除meta, 是一个list, 包含了所有需要删除内容的`mid` | ✅ | `[1, 2, 3]` |
- **返回值示例**:
    ```json
    {
        "code": 1,
        "message": "token correct",
        "add": [
            {
                "code": 1,
                "message": "succeed",
                "mid": 23,
                "hash": 546782
            }
        ],
        "update": [
            {
                "code": 1,
                "message": "succeed",
                "mid": 12
            }
        ],
        "delete": [
            {
                "code": 1,
                "message": "succeed",
                "mid": 7
            }
        ]
    }
    ```
- **返回值说明**
  | 返回值  |           说明            | 数据格式 |     示例      |
  | :-----: | :-----------------------: | :------: | :-----------: |
  |  code   | 状态码, 1为成功, -1为失败 |   int    |       1       |
  | message |           消息            |  string  | token correct |
  |   add   |    增加meta的状态返回     |   list   |      略       |
  | update  |    meta修改的状态返回     |   list   |      略       |
  | delete  |    删除meta的状态返回     |   list   |      略       |
- **增加文章状态返回参数说明**
  | 返回值  |               说明                | 数据格式 |  示例   |
  | :-----: | :-------------------------------: | :------: | :-----: |
  |  code   |     状态码, 1为成功, -1为失败     |   int    |    1    |
  | message |    消息, 失败则返回数据库报错     |  string  | succeed |
  |   mid   | 成功后返回新meta的mid, 失败返回-1 |   int    |   234   |
  |  hash   |   同/push的参数列表中add的hash    |   int    | 346252  |
- **文章修改状态返回参数说明**
  | 返回值  |            说明            | 数据格式 |  示例   |
  | :-----: | :------------------------: | :------: | :-----: |
  |  code   | 状态码, 1为成功, -1为失败  |   int    |    1    |
  | message | 消息, 失败则返回数据库报错 |  string  | succeed |
  |   mid   |       操作meta的mid        |   int    |   234   |
- **删除文章状态返回参数说明**
  | 返回值  |            说明            | 数据格式 |  示例   |
  | :-----: | :------------------------: | :------: | :-----: |
  |  code   | 状态码, 1为成功, -1为失败  |   int    |    1    |
  | message | 消息, 失败则返回数据库报错 |  string  | succeed |
  |   mid   |       删除meta的mid        |   int    |   234   |

## POST /push_relationships

- **功能**: 更新文章和页面与标签和类别匹配的数据
- **参数列表**:
    | 参数  | 说明  | 可选  | 示例  |
    | :---: | :---: | :---: | :---: |
    | token | 用于请求验证 | ✅ | your_token |
    | add | 增加匹配, 是一个list。每个元素由一对`cid`与`mid`构成 | ✅ | `[{"cid": 5, "mid": 3}, {"cid": 5, "mid": 4}]` |
    | delete | 删除匹配, 是一个list, 包含了所有需要删除匹配二元组 | ✅ | `[{"cid": 5, "mid": 3}, {"cid": 5, "mid": 4}]` |
- **返回值示例**:
    ```json
    {
        "code": 1,
        "message": "token correct",
        "add": [
            {
                "code": 1,
                "message": "succeed",
                "cid": 23,
                "mid": 123
            }
        ],
        "delete": [
            {
                "code": 1,
                "message": "succeed",
                "cid": 24,
                "mid": 13
            }
        ]
    }
    ```
- **返回值说明**
  | 返回值  |           说明            | 数据格式 |     示例      |
  | :-----: | :-----------------------: | :------: | :-----------: |
  |  code   | 状态码, 1为成功, -1为失败 |   int    |       1       |
  | message |           消息            |  string  | token correct |
  |   add   |    增加匹配的状态返回     |   list   |      略       |
  | delete  |    删除匹配的状态返回     |   list   |      略       |
- **增加文章状态返回参数说明**
  | 返回值  |            说明            | 数据格式 |  示例   |
  | :-----: | :------------------------: | :------: | :-----: |
  |  code   | 状态码, 1为成功, -1为失败  |   int    |    1    |
  | message | 消息, 失败则返回数据库报错 |  string  | succeed |
  |   cid   |         匹配的cid          |   int    |   234   |
  |   mid   |         匹配的mid          |   int    |   343   |
- **删除文章状态返回参数说明**
  | 返回值  |            说明            | 数据格式 |  示例   |
  | :-----: | :------------------------: | :------: | :-----: |
  |  code   | 状态码, 1为成功, -1为失败  |   int    |    1    |
  | message | 消息, 失败则返回数据库报错 |  string  | succeed |
  |   cid   |         匹配的cid          |   int    |   234   |
  |   mid   |         匹配的mid          |   int    |   343   |
