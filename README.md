# TodoBot

饭否 Todo 机器人，添加 Todo 事项后在指定时间发送消息/私信提醒未完成的事项。

# 使用说明

可以通过给 [@TodoBot](http://fanfou.com/todobot) 发送消息或私信来创建/管理 Todo list.

# FAQ

1. Q: 为什么任务过期了还会提醒？A: 只要任务没有完成，即使过期也会继续提醒，所以如果做完了记得[标记成已完成](#完成任务)；或者[修改截止日期](#修改截止日期)；或者[删除任务](#删除任务)。

2. Q: 怎么关闭提醒？A: 给@TodoBot发送`!msg off`。如果想恢复每天的提醒，给@TodoBot发送`!msg public`或`!msg private`，见[修改提醒方式](#修改提醒方式)。

3. Q: 为什么不能给@TodoBot发送私信？A: 很可能是因为你在用某个客户端，饭否API需要有相应的权限才能发送私信，见[饭否API文档](https://github.com/FanfouAPI/FanFouAPIDoc/wiki/direct-messages.new)。网页版可以正常发送私信。

## 消息类型

### 命令消息

所有命令消息都是`!cmd`形式（**注意是半角的感叹号**)，目前一共有 7 种命令:

1. 获取任务列表: `!list [todo/all/done(finished)]`
2. 删除任务: `!del[ete] task_id`
3. 完成任务: `!finish(done) task_id`
4. 修改截止日期: `!due task_id due_date`
5. 修改提醒方式: `!msg public/private/off`
6. 修改提醒时间: `!msg task_id remind_time`
7. 修改提醒频率: `!freq task_id once/daily/weekly/monthly/yearly`

命令消息格式:

#### 获取任务列表

    !list [todo/all/done(finished)]

- `todo`: 返回尚未开始的任务，`todo`也是新创建任务的默认状态
- `all`: 返回所有任务，包括`todo`和`done`两种状态
- `done(finished)`: 两个参数含义一样，返回已完成的任务

默认参数为`todo`，返回的任务按截止日期从近到远排列

#### 删除任务

    !del[ete] task_id

- `task_id`: `!list`命令返回的任务列表中，相应任务的序号

`!del`命令会将任务从数据库中彻底删除

#### 完成任务

    !done(finish) task_id

- `task_id`: `!list`命令返回的任务列表中，相应任务的序号

将任务状态改为`done`，不再包含在提醒消息中

#### 修改截止日期

    !due task_id due_date

- `task_id`: `!list`命令返回的任务列表中，相应任务的序号
- `due_date`: 日期，格式参见 [`dateparser`](https://github.com/scrapinghub/dateparser) 支持的格式，包括一些自然语言格式，比如"in 2 days"会解析为两天（48小时）之后。不过还是建议用数字形式，否则可能会解析成错误的结果。支持的数字形式也比较灵活，比如常见的"2017.6.10 13:30"/"20:40"，不加年份默认为当年，不加日期默认为当天

示例:

- `!due 3 13:30`
- `!due 2 2018.3.12`
- `!due 5 in 3 days`

#### 修改提醒方式

    !msg public/private/off

- `public`: 通过@发送提醒消息
- `private`: 通过私信发送提醒消息
- `off`: 停止发送定时提醒消息

当新用户加入时，如果通过私信创建任务，默认通过私信提醒，如果通过@TodoBot创建任务，默认通过@提醒，可以通过`!msg`命令更改提醒方式

不管选择什么提醒方式，都可以通过私信或@来发送命令或创建任务，不过**即使是通过私信发送的消息，如果设置的提醒方式是@，仍然有可能在TodoBot发送回复的时候被其他人看到**

#### 修改提醒时间

    !remind task_id remind_time

- `task_id`: `!list`命令返回的任务列表中，相应任务的序号
- `remind_time`: 下次提醒时间，格式见[修改截止日期](#修改截止日期)。需大于当前时间，否则修改了也没用

#### 修改提醒频率

    !freq task_id once/hourly/daily/weekly/monthly/yearly

- `task_id`: `!list`命令返回的任务列表中，相应任务的序号
- `once`: 只提醒一次
- `hourly`: 每小时提醒一次
- `daily`: 每天提醒一次
- `weekly`: 每周提醒一次
- `monthly`: 每月提醒一次
- `yearly`: 每年提醒一次

### 新建任务

所有非命令类消息都默认是新任务，格式如下:

    task [| due_date | remind_time | remind_frequency]

- `task`: 任务描述
- `due_date`: 任务截止日期，格式见[修改截止日期](#修改截止日期)，可选，如果有`due_date`，在`task`之后添加竖线`|`分隔
- `remind_time`: 下次提醒时间，可选，默认是第二天早上`7:30`
- `remind_frequency`: 提醒频率，可选，选项见[修改提醒频率](#修改提醒频率)，默认是每天提醒

如果中间某些列用默认设置，后面要用自定义设置，默认设置列对应的`|`也需要给出来

示例:

- `跑步 || 19:00 | daily` (没有`due_date`，但第二条`|`必须有)
- `修改ppt | 4.18 13:00`
- `半铁 | 2018.6.30`

# Todo

TodoBot 的 Todo……

1. 支持修改非`todo`状态的任务，目前为了保持命令序号和每天提醒里的任务序号一致，只支持修改`todo`状态的任务
~~2. 支持单个任务的提醒（如截止时间前半小时发送提醒消息），目前只能每天提醒所有未完成的任务~~ (done)
3. 批量操作任务（删除/修改状态等）
~~4. 支持创建定期重复的任务~~ (变相done)

# 致谢

`fanfou.py` 和部分代码来自 [`fanfou-bot`](https://github.com/akgnah/fanfou-bot) 项目
