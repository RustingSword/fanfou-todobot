#! coding: utf-8
from flask import request, url_for, jsonify
from . import app
from .task import parse_msg, format_task_list
from .models import db, User, Task, MessageID
from .message import FanfouClient
from datetime import datetime
from dateutil import parser

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

def htmlec(s):
    el = {'&lt;': '<', '&gt;': '>', '&quot;': '"', '&amp;': '&'}
    for k, v in el.items():
        s = s.replace(k, v)
    return s

def check_msg(msg_num):
    newest_msg = MessageID.query.filter_by(name='msg').first()
    if newest_msg:
        newest_msg_id = newest_msg.message_id
        newest_msg_ts = newest_msg.message_ts
    else:
        newest_msg_id = None
        newest_msg_ts = datetime.fromtimestamp(0)
        newest_msg = MessageID(name='msg', message_id='',
                message_ts=newest_msg_ts)
        db.session.add(newest_msg)
    count = min(60, msg_num)
    pages = msg_num / count + 2
    processed_msg = 0
    for page in range(1, pages):
        messages = client.get_msg_list(count, page, newest_msg_id)
        for item in messages:
            msg_timestamp = parser.parse(item['created_at']).replace(tzinfo=None)
            if newest_msg_ts < msg_timestamp:
                newest_msg_ts = msg_timestamp
                newest_msg_id = item['id']
            if not item['text'].startswith('@TodoBot'):
                continue
            text = item['text'].replace('@TodoBot ', '').strip()
            text = text.replace('@', '#')
            user_id = item['user']['id']
            user_name = item['user']['name']
            reply = parse_msg(user_id, text, user_name)
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

def check_dm(dm_num):
    newest_msg = MessageID.query.filter_by(name='dm').first()
    if newest_msg:
        newest_msg_id = newest_msg.message_id
        newest_msg_ts = newest_msg.message_ts
    else:
        newest_msg_id = None
        newest_msg_ts = datetime.fromtimestamp(0)
        newest_msg = MessageID(name='dm', message_id='',
                message_ts=newest_msg_ts)
        db.session.add(newest_msg)
    count = min(60, dm_num)
    pages = dm_num / count + 2
    processed_dm = 0
    for page in range(1, pages):
        direct_messages = client.get_dm_list(count, page, newest_msg_id)
        for item in direct_messages:
            msg_timestamp = parser.parse(item['created_at']).replace(tzinfo=None)
            if newest_msg_ts < msg_timestamp:
                newest_msg_ts = msg_timestamp
                newest_msg_id = item['id']
            text = htmlec(item['text'].strip())
            text = text.replace('@', '#')
            user_id = item['sender']['id']
            user_name = item['sender']['name']
            client.delete_dm(item['id'])
            reply = parse_msg(user_id, text, user_name, 'private')
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                reply = u'没有任务'
            if not user or user.msg_type == 'private':
                client.send_dm(reply, user_id)
            else:
                client.send_msg(reply, user_id, user_name)
            processed_dm += 1
    newest_msg.message_id = newest_msg_id
    newest_msg.message_ts = newest_msg_ts
    db.session.commit()
    return processed_dm

@app.route('/check')
def check():
    msg_num, dm_num = client.get_notification()
    processed_msg = processed_dm = 0
    if msg_num > 0:
        processed_msg = check_msg(msg_num)
    if dm_num > 0:
        processed_dm = check_dm(dm_num)
    return 'done checking, #msg %d #dm %d' % (processed_msg, processed_dm)

@app.route('/notify')
def notify():
    users = User.query.all()
    for user in users:
        tasks = Task.query.filter_by(user=user).filter_by(status='todo').all()
        if not tasks:
            continue
        if user.msg_type == 'private':
            client.send_dm(format_task_list(tasks), user.user_id)
        elif user.msg_type == 'public':
            client.send_msg(format_task_list(tasks), user.user_id, user.user_name)
    return 'finished daily notification for %d users' % len(users)
