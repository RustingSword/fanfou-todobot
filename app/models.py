#! coding: utf-8
''' database definition '''
from datetime import datetime
from . import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True)
    user_name = db.Column(db.String(80), nullable=True)
    # public: 通过@发送消息
    # private: 通过私信发送消息
    msg_type = db.Column(db.String(10), default='public')

    def __repr__(self):
        return '<User %r>' % self.user_id

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    # task status, may be one of 'todo'/'done'
    status = db.Column(db.String(10), nullable=False, default='todo')
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now,
                            onupdate=datetime.now)
    reminder_time = db.Column(db.DateTime)
    # 'once', 'hourly', 'daily', 'weekly', 'monthly', 'yearly'
    reminder_frequency = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('tasks', lazy='dynamic'))
    __mapper_args__ = {
        "order_by": due_date
    }

    def brief_info(self):
        ''' brief info used in notification '''
        return '%s%s%s' % (
            self.task,
            ' | status: ' + self.status,
            ' | due: ' + self.due_date.strftime('%F %T') if self.due_date else ''
        )

    def detail_info(self):
        ''' detail info used in list command '''
        return '%s | status: %s | due: %s | remind: %s | freq: %s' % (
            self.task,
            self.status,
            self.due_date.strftime('%F %T') if self.due_date else '',
            self.reminder_time.strftime('%F %T') if self.reminder_time else '',
            self.reminder_frequency
        )

    def __repr__(self):
        return self.detail_info()

class MessageID(db.Model):
    __tablename__ = 'messageid'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    message_id = db.Column(db.String, nullable=False)
    message_ts = db.Column(db.DateTime, nullable=False)
