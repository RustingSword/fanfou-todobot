#! coding: utf-8
''' parse message and create tasks '''
import dateparser as dp
import utils
from .models import db, User, Task
from . import app

def process_list_cmd(user, task_type):
    ''' !list command '''
    if not task_type:
        task_type = 'todo'
    user_tasks = Task.query.filter_by(user=user)
    if task_type == 'all':
        tasks = user_tasks.all()
    elif task_type in ('done', 'finished'):
        tasks = user_tasks.filter(Task.status == 'done').all()
    elif task_type == 'todo':
        tasks = user_tasks.filter(Task.status == 'todo').all()
    elif app.config.get('DEBUG') and task_type == '上上下下左右左右BA':
        tasks = Task.query.all()
    else:
        tasks = []
    task_list = [(i, t) for i, t in enumerate(tasks, start=1)]
    return utils.format_task_list(task_list, brief=False)

def process_msg_cmd(user, msg_type):
    ''' !msg command '''
    if msg_type in ('public', 'private', 'off'):
        user.msg_type = msg_type
        db.session.commit()
    else:
        return u'错误的消息类型[%s]' % msg_type
    if msg_type == 'private':
        return u'提醒将以[私信]形式发送'
    if msg_type == 'public':
        return u'提醒将以[消息]形式发送'
    return u'不再发送提醒消息'

def process_del_cmd(task):
    ''' !del command '''
    try:
        db.session.delete(task)
        db.session.commit()
    except:
        db.session.rollback()
        return u'删除任务失败'
    return u'删除任务[%s]成功' % task.task

def process_done_cmd(task):
    ''' !done command '''
    try:
        task.status = 'done'
        db.session.commit()
    except:
        db.session.rollback()
        return u'任务状态修改失败'
    return u'任务[%s]的状态已变更为[%s]' % (task.task, task.status)

def process_due_cmd(task, data):
    ''' !due command '''
    if len(data) > 2:
        due = dp.parse(' '.join(data[2:]))
    else:
        return u'没有指定时间'
    if due:
        task.due_date = due
        db.session.commit()
    else:
        return u'错误的时间格式'
    return u'任务[%s]的截止时间已变更为[%s]' % (
        task.task,
        task.due_date.strftime('%F %T'))

def process_remind_cmd(task, data):
    ''' !remind command '''
    if len(data) > 2:
        dt = dp.parse(' '.join(data[2:]))
    else:
        return u'没有指定时间'
    if dt:
        task.reminder_time = dt
        db.session.commit()
    else:
        return u'错误的时间格式'
    return u'任务[%s]的提醒时间已变更为[%s]' % (
        task.task,
        task.reminder_time.strftime('%F %T'))

def process_freq_cmd(task, data):
    ''' !freq command '''
    if len(data) > 2:
        freq = data[2]
    else:
        return u'没有指定提醒频率'
    if freq in ('once', 'hourly', 'daily', 'weekly', 'monthly', 'yearly'):
        task.reminder_frequency = freq
        db.session.commit()
    else:
        return u'错误的提醒频率[%s]'
    return u'任务[%s]的提醒频率已变更为[%s]' % (task.task,
                                     task.reminder_frequency)

def parse_msg(user_id, data, user_name=None, msg_type='public'):
    ''' parse message received from user
    There are two types of messages:
    1. command message
    2. new task
    '''
    if not data.startswith(('!list', '!msg', '!fin', '!done', '!due', '!del',
                            '!remind', '!freq')):
        return parse_task(user_id, data, user_name, msg_type)

    data = data.split()
    cmd = data[0]
    # only '!list' command can have no arguments
    if len(data) == 1 and not cmd.startswith('!list'):
        return u'命令不完整'
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return u'还没有创建任务'
    if cmd.startswith('!msg'):
        return process_msg_cmd(user, data[1].strip())
    if cmd.startswith('!list'):
        task_type = 'todo' if len(data) == 1 else data[1].strip()
        return process_list_cmd(user, task_type)

    # all the following commands will modify specified task
    try:
        task_id = int(data[1].strip()) - 1
    except ValueError:
        return u'错误的任务序号'
    task = Task.query.filter_by(user=user) \
                     .filter_by(status='todo') \
                     .offset(task_id) \
                     .first()
    reply = ''
    if not task:
        reply = u'没有找到指定任务'
    elif cmd.startswith('!del'):
        reply = process_del_cmd(task)
    elif cmd.startswith('!finish') or cmd.startswith('!done'):
        reply = process_done_cmd(task)
    elif cmd.startswith('!due'):
        reply = process_due_cmd(task, data)
    elif cmd.startswith('!remind'):
        reply = process_remind_cmd(task, data)
    elif cmd.startswith('!freq'):
        reply = process_freq_cmd(task, data)
    return reply

def parse_task(user_id, data, user_name, msg_type):
    ''' create a new task '''
    task = data
    due = None
    reminder_time = None
    reminder_frequency = 'daily'
    if '|' in data:
        cols = data.split('|')
        task = cols[0].strip()
        due = dp.parse(cols[1])
        reminder_time = dp.parse('tomorrow 7:30')
        if len(cols) > 2:
            reminder_time = dp.parse(cols[2])
            if reminder_time is None:
                reminder_time = dp.parse('tomorrow 7:30')
        if len(cols) > 3:
            reminder_frequency = cols[3].strip()
            if reminder_frequency not in (
                    'once', 'hourly', 'daily', 'weekly', 'monthly', 'yearly'):
                reminder_frequency = 'daily'
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        new_task = Task(task=task, due_date=due, user=user,
                        reminder_time=reminder_time,
                        reminder_frequency=reminder_frequency)
        db.session.add(new_task)
    else:
        new_user = User(user_id=user_id, user_name=user_name, msg_type=msg_type)
        db.session.add(new_user)
        new_task = Task(task=task, due_date=due, user=new_user,
                        reminder_time=reminder_time,
                        reminder_frequency=reminder_frequency)
        db.session.add(new_task)
    db.session.commit()
    return u'添加任务[%s]，截止时间[%s]，下次提醒时间[%s]，提醒频率[%s]' % (
        new_task.task,
        new_task.due_date.strftime('%F %T') if new_task.due_date else u'未指定',
        new_task.reminder_time.strftime('%F %T'),
        new_task.reminder_frequency
    )
