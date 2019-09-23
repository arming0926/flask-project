# ArminBlog

*Armin blog.*

# Installation

### 安装项目相关依赖包
```
$ pip install -r requirements.txt
```

### 创建数据库相关表
```
# 用户表：
create table verify_users(
   id INT NOT NULL AUTO_INCREMENT,
   tel VARCHAR(11) NOT NULL,
   password VARCHAR(15) NOT NULL,
   PRIMARY KEY ( id )
);

# 日志表：
CREATE TABLE user_blog(title VARCHAR(30) NOT NULL, author VARCHAR(10) NOT NULL,update_time VARCHAR(50) NOT NULL, content longtext  NOT NULL);
alter table user_blog modify column content longtext not null;

# 个人资料表：
CREATE TABLE personal_info(id int primary key auto_increment,name VARCHAR(50),sex VARCHAR(10),age int, nation VARCHAR(20),address VARCHAR(200),email VARCHAR(100),wechat VARCHAR(100),hobby VARCHAR(100));
alter table personal_info modify column hobby longtext;
```
### 启动项目
```
$ python3 run.py
* Running on http://127.0.0.1:5000/
```
