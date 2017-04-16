#! coding: utf-8
from .models import db, User, Task
from . import app
import dateparser as dp

def format_task_list(tasks):
    if tasks:
        return '\n'.join([
            '%d %s | %s' % (i + 1, t.task, t.due_date.strftime('%F %T') if
                t.due_date else '') for i, t in enumerate(tasks)]
        )
    return u'没有任务'

def parse_msg(user_id, data, user_name=None, msg_type='public'):
    ''' parse message received from user
    There are two types of messages:
    1. command message
    2. new task
    '''
    if not any([data.startswith('!list'), data.startswith('!msg'),
        data.startswith('!finish'), data.startswith('!done'),
        data.startswith('!due'), data.startswith('!del')]):
        return parse_task(user_id, data, user_name, msg_type)

    user = User.query.filter_by(user_id=user_id).first()
    if data.startswith('!msg'):
        msg_type = data.split()[1].strip()
        if msg_type in ('public', 'private'):
            user.msg_type = msg_type
            db.session.commit()
        else:
            return u'错误的消息类型'
        if msg_type == 'private':
            return u'提醒将以[私信]形式发送'
        else:
            return u'提醒将以[消息]形式发送'

    if data.startswith('!list'):
        data = data.split()
        task_type = data[1] if len(data) > 1 else 'todo'
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
        return format_task_list(tasks)

    # all the following command will modify specified task
    data = data.split()
    if len(data) < 2:
        return u'没有指定任务序号'
    command = data[0]
    task_id = int(data[1]) - 1
    task = Task.query.filter_by(user=user).offset(task_id).first()
    if not task:
        return u'没有找到指定任务'
    if command.startswith('!del'):
        try:
            db.session.delete(task)
            db.session.commit()
        except:
            db.session.rollback()
            return u'删除任务失败'
        return u'删除任务[%s]成功' % task.task
    if command.startswith('!finish') or command.startswith('!done'):
        try:
            task.status = 'done'
            db.session.commit()
        except:
            db.session.rollback()
            return u'任务状态修改失败'
        return u'任务[%s]的状态已变为[%s]' % (task.task, task.status)
    if command.startswith('!due'):
        if len(data) > 2:
            due = dp.parse(' '.join(data[2:]))
        else:
            return u'没有指定时间'
        if due:
            task.due_date = due
            db.session.commit()
        else:
            return u'错误的时间格式'
        return u'任务[%s]的截止时间已变为[%s]' % (task.task,
                task.due_date.strftime('%F %T'))

def parse_task(user_id, data, user_name, msg_type):
    if '|' in data:
        task, due = data.split('|')
        task = task.strip()
        due = dp.parse(due)
    else:
        task, due = data, None
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        new_task = Task(task=task, due_date=due, user=user)
        db.session.add(new_task)
    else:
        new_user = User(user_id=user_id, user_name=user_name, msg_type=msg_type)
        db.session.add(new_user)
        new_task = Task(task=task, due_date=due, user=new_user)
        db.session.add(new_task)
    db.session.commit()
    return u'添加任务[%s]，截止时间为[%s]' % (
        new_task.task,
        new_task.due_date.strftime('%F %T') if new_task.due_date else u'未指定'
    )
