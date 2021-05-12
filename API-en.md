!!! TRANSLATION STILL IN PROCESS !!!

# typecho Database Design

Official documentation about database of typecho is here: https://docs.typecho.org/database

Due to the reason that the official document is quite ambiguous and lack detailed explanation, here are some extra details.

## typecho_contents

**Function**: Store pages and posts

|     key     |     type     |       attributes       |               interpretation                |
| :----------: | :----------: | :--------------: | :-------------------------------: |
|     cid      |   int(10)    |  primary key, nonnegative, AUTO_INCREMENT  |            primary key of contents table             |
|    title     | varchar(200) |      nullable      |             title              |
|     slug     | varchar(200) |   index,nullable    |            abbreviation for title             |
|   created    |   int(10)    | index,nonnegative,nullable |    GMT unix timestamp when created     |
|   modified   |   int(10)    |   nonnegative,nullable    |    GMT unix timestamp when modified     |
|     text     |     text     |      nullable      |             content              |
|    order     |   int(10)    |   nonnegative,nullable    |            sort          |
|   authorId   |   int(10)    |   nonnegative,nullable    |          user id of author           |
|   template   | varchar(32)  |      nullable      |          template used           |
|     type     | varchar(16)  |      nullable      |             type of content              |
|    status    | varchar(16)  |      nullable      |             status of content              |
|   password   | varchar(32)  |      nullable      | password if protected |
| commentsNum  |   int(10)    |   nonnegative,nullable    |      count of comments, redundant      |
| allowComment |   char(1)    |      nullable      |           whether allow comment            |
|  allowPing   |   char(1)    |      nullable      |           whether allow ping            |
|  allowFeed   |   char(1)    |      nullable      |         whether allow feed          |
