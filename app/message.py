#! coding: utf-8
''' fanfou client for receiving/sending messages '''
from __future__ import print_function
import json
import math
import fanfou

class FanfouClient:
    ''' fanfou client based on fanfou.py '''
    def __init__(self, consumer_token, access_token):
        self.client = fanfou.OAuth(consumer_token, access_token)

    def get_notification_num(self):
        ''' get the unread number of mention/direct messages '''
        body = dict(mode='lite')
        try:
            resp = self.client.request('/account/notify_num', 'GET', body)
        except Exception as e:
            print('error getting notification: ' + repr(e))
            return 0
        data = json.loads(resp.read())
        return data.get('notify_num', 0)

    def get_notification(self):
        ''' get the unread number of mention/direct messages '''
        body = dict(mode='lite')
        try:
            resp = self.client.request('/account/notification', 'GET', body)
        except Exception as e:
            print('error getting notification: ' + repr(e))
            return 0, 0
        data = json.loads(resp.read())
        return data.get('mentions', 0), data.get('direct_messages', 0)

    def get_msg_list(self, count=20, page=1, since_id=None):
        ''' get mention message list '''
        body = dict(count=count, page=page, mode='lite')
        if since_id:
            body['since_id'] = since_id
        try:
            resp = self.client.request('/statuses/mentions', 'GET', body)
        except Exception as e:
            print('error getting msg list: ' + repr(e))
            return []
        return json.loads(resp.read())

    def get_dm_list(self, count=20, page=1, since_id=None):
        ''' get direct message list '''
        body = dict(count=count, page=page, mode='lite')
        if since_id:
            body['since_id'] = since_id
        try:
            resp = self.client.request('/direct_messages/inbox', 'GET', body)
        except Exception as e:
            print('error getting dm list: ' + repr(e))
            return []
        return json.loads(resp.read())

    def split_msg(self, msg, piece_len=130):
        ''' split message into pieces shorter than 140 characters '''
        assert piece_len <= 140
        if len(msg) <= piece_len:
            return [msg.encode('utf-8')]
        num_msg_piece = int(math.ceil(len(msg) * 1.0 / piece_len))
        msg_pieces = [
            msg[piece_len * p: piece_len * p + piece_len].encode('utf-8') for \
                    p in range(num_msg_piece)
        ]

        return msg_pieces

    def send_msg(self, msg='test', user_id=None, user_name=None):
        ''' send metion message '''
        user_name = user_name.encode('utf-8')
        user_id = user_id.encode('utf-8')
        if len(msg) > 140:
            msg_pieces = self.split_msg(msg)
            for i, piece in enumerate(msg_pieces):
                body = {
                    'status': '@%s (%d/%d) %s' % (user_name, i+1, len(msg_pieces), piece),
                    'in_reply_to_user_id': user_id,
                    'mode': 'lite'
                }
                try:
                    self.client.request('/statuses/update', 'POST', body)
                except Exception as e:
                    print('error sending msg: ' + repr(e))
        else:
            body = {
                'status': '@%s %s' % (user_name, msg.encode('utf-8')),
                'in_reply_to_user_id': user_id,
                'mode': 'lite'
            }
            try:
                self.client.request('/statuses/update', 'POST', body)
            except Exception as e:
                print('error sending msg: ' + repr(e))

    def send_dm(self, msg='test', user_id=None):
        ''' send direct message '''
        user_id = user_id.encode('utf-8')
        if len(msg) > 140:
            msg_pieces = self.split_msg(msg)
            for i, piece in enumerate(msg_pieces):
                body = {
                    'user': user_id,
                    'text': '(%d/%d) %s' % (i + 1, len(msg_pieces), piece),
                    'mode': 'lite'
                }
                try:
                    self.client.request('/direct_messages/new', 'POST', body)
                except Exception as e:
                    print('error sending dm: ' + repr(e))
        else:
            body = {
                'user': user_id,
                'text': msg.encode('utf-8'),
                'mode': 'lite'
            }
            try:
                self.client.request('/direct_messages/new', 'POST', body)
            except Exception as e:
                print('error sending dm: ' + repr(e))

    def delete_dm(self, dm_id):
        ''' delete received direct message '''
        try:
            self.client.request('/direct_messages/destroy', 'POST', {'id': dm_id})
        except Exception as e:
            print('error deleting dm: ' + repr(e))
