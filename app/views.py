#! coding: utf-8
''' views definition '''
from datetime import datetime
from dateutil import parser
from flask import request, url_for, jsonify
import utils
from . import app
from .task import parse_msg
from .models import db, User, Task, MessageID
from .message import FanfouClient

client = FanfouClient(
    {
        'key': app.config.get('FANFOU_CONSUMER_KEY'),
        'secret': app.config.get('FANFOU_CONSUMER_SECRET')
    },
    {
        'key': app.config.get('FANFOU_AUTH_KEY'),
        'secret': app.config.get('FANFOU_AUTH_SECRET')
    }
)

def check_msg(msg_num, msg_type='msg'):
    if msg_type not in ('msg', 'dm'):
        return 0
    newest_msg = MessageID.query.filter_by(name=msg_type).first()
    if newest_msg:
        newest_msg_id = newest_msg.message_id
        newest_msg_ts = newest_msg.message_ts
    else:
        newest_msg_id = None
        newest_msg_ts = datetime.fromtimestamp(0)
        newest_msg = MessageID(name=msg_type, message_id='',
                               message_ts=newest_msg_ts)
        db.session.add(newest_msg)
    count = min(60, msg_num)
    pages = msg_num / count + 2
    processed_msg = 0
    for page in range(1, pages):
        if msg_type == 'msg':
            messages = client.get_msg_list(count, page, newest_msg_id)
        else:
            messages = client.get_dm_list(count, page, newest_msg_id)
        for item in messages:
            msg_ts = parser.parse(item['created_at']).replace(tzinfo=None)
            if newest_msg_ts < msg_ts:
                newest_msg_ts = msg_ts
                newest_msg_id = item['id']
            if msg_type == 'msg' and not item['text'].startswith('@TodoBot'):
                continue
            text = utils.htmlec(item['text'].replace('@TodoBot ', '').strip())
            text = text.replace('@', '#')
            if msg_type == 'msg':
                user_id = item['user']['id']
                user_name = item['user']['name']
                reply = parse_msg(user_id, text, user_name)
            else:
                user_id = item['sender']['id']
                user_name = item['sender']['name']
                reply = parse_msg(user_id, text, user_name, 'private')
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                reply = u'没有任务'
            if not user or user.msg_type == 'public':
                client.send_msg(reply, user_id, user_name)
            else:
                client.send_dm(reply, user_id)
            processed_msg += 1
    newest_msg.message_id = newest_msg_id
    newest_msg.message_ts = newest_msg_ts
    db.session.commit()
    return processed_msg

@app.route('/check')
def check():
    ''' check for new mention messages and direct messages '''
    msg_num, dm_num = client.get_notification()
    processed_msg = processed_dm = 0
    if msg_num > 0:
        processed_msg = check_msg(msg_num)
    if dm_num > 0:
        processed_dm = check_msg(dm_num, msg_type='dm')
    return 'done checking, #msg %d #dm %d' % (processed_msg, processed_dm)

@app.route('/notify')
def notify():
    ''' send notification for tasks scheduled '''
    users = User.query.all()
    now = datetime.now()
    for user in users:
        tasks = Task.query.filter_by(user=user).filter_by(status='todo').all()
        to_notify = [
            t for t in tasks if utils.should_notify(now, t.reminder_time)
        ]
        if not to_notify:
            continue
        if user.msg_type == 'private':
            client.send_dm(utils.format_task_list(to_notify), user.user_id)
        elif user.msg_type == 'public':
            client.send_msg(utils.format_task_list(to_notify), user.user_id,
                            user.user_name)
        for task in to_notify:
            task.reminder_time = utils.next_notify_ts(task.reminder_time,
                                                      task.reminder_frequency)
    db.session.commit()
    return 'finished notification for %d users' % len(users)
