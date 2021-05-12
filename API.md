# typexo服务器API文档

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
    | 参数  | 说明  | 可选  | 示例  |
    | :---: | :---: | :---: | :---: |
    | token | 用于请求验证 | ✔ | your_token |
- **返回值示例**:
    ```json
    {
        "code": 1,
        "message": "hello world"
    }
    ```
- **返回值说明**:
  | 返回值 | 说明 | 数据格式 | 示例 |
  | :---: | :---: | :---: | :---: |
  | code | 状态码, 1为成功, -1为失败 | int | 1 |
  | message | 消息 | string | hello world |

## GET /fetch

- **功能**: 拉取服务端的文章数据
- **参数列表**:
    | 参数  | 说明  | 可选  | 示例  |
    | :---: | :---: | :---: | :---: |
    | token | 用于请求验证 | ✔ | your_token |
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
                "template": "post",
                "status": "publish",
                "password": null,
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
                "template": "page",
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
- **返回值说明**:
  | 返回值 | 说明 | 数据格式 | 示例 |
  | :---: | :---: | :---: | :---: |
  | code | 状态码, 1为成功, -1为失败 | int | 1 |
  | message | 消息, 成功为"succeed" | string | succeed |
  | data | 文章数据, 请参照typecho SQL设计解释 | list | 略 |

## GET /push

- **功能**: 更新数据
- **参数列表**:
    | 参数  | 说明  | 可选  | 示例  |
    | :---: | :---: | :---: | :---: |
    | token | 用于请求验证 | ✔ | your_token |
    | add | 增加文章/页面, 是一个list。每个元素都有两个键值, 第一个键值为`hash`, 作为验证, 在本次增加的所有数据中应具有唯一性；第二个键值为`data`, 数据格式请参照typecho SQL设计解释 | ✔ | `[{"hash": 1323795, "data": <page_data_1>}, {"hash": 437289, "data": <page_data_2>}, ...]`
    | update | 更改已有文章/页面, 是一个list。每个元素都有两个键值, 第二个键值为文章`cid`, 第二个键值为`data`, 数据格式请参照typecho SQL设计解释。注：这里数据不需完全, 只需包含更改的条目 | ✔ | `[{"cid": 1, "data": <page_data_1>}, {"cid": 2, "data": <page_data_2>}, ...]` |
    | delete | 删除文章/页面, 是一个list, 包含了所有需要删除内容的`cid` | ✔ | `[1, 2, 3]`
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
  | 返回值 | 说明 | 数据格式 | 示例 |
  | :---: | :---: | :----: | :--: |
  | code | 状态码, 1为成功, -1为失败 | int | 1 |
  | message | 消息 | string | token correct |
  | add | 增加文章的状态返回 | list | 略 |
  | update | 文章修改的状态返回 | list | 略 |
  | delete | 删除文章的状态返回 | list | 略 |
- **增加文章状态返回参数说明**
  | 返回值 | 说明 | 数据格式 | 示例 |
  | :---: | :---: | :----: | :--: |
  | code | 状态码, 1为成功, -1为失败 | int | 1 |
  | message | 消息, 失败则返回数据库报错 | string | succeed |
  | cid | 成功后返回新文章的cid, 失败返回-1 | int | 234 |
  | hash | 同/push的参数列表中add的hash | int | 346252 |
- **文章修改状态返回参数说明**
  | 返回值 | 说明 | 数据格式 | 示例 |
  | :---: | :---: | :----: | :--: |
  | code | 状态码, 1为成功, -1为失败 | int | 1 |
  | message | 消息, 失败则返回数据库报错 | string | succeed |
  | cid | 操作文章的cid | int | 234 |
- **删除文章状态返回参数说明**
  | 返回值 | 说明 | 数据格式 | 示例 |
  | :---: | :---: | :----: | :--: |
  | code | 状态码, 1为成功, -1为失败 | int | 1 |
  | message | 消息, 失败则返回数据库报错 | string | succeed |
  | cid | 操作文章的cid | int | 234 |

# typecho SQL设计解释

