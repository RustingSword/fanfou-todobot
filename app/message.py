#! coding: utf-8
from . import app
import fanfou
import json
import math

class FanfouClient:
    def __init__(self):
        self.client = fanfou.OAuth(
            {
                'key': app.config.get('FANFOU_CONSUMER_KEY'),
                'secret': app.config.get('FANFOU_CONSUMER_SECRET')
            },
            {
                'key': app.config.get('FANFOU_AUTH_KEY'),
                'secret': app.config.get('FANFOU_AUTH_SECRET')
            }
        )

    def get_notification(self):
        body = dict(mode='lite')
        resp = self.client.request('/account/notification', 'GET', body)
        data = json.loads(resp.read())
        return data.get('mentions', 0), data.get('direct_messages', 0)

    def get_msg_list(self, count=20, page=1, since_id=None):
        body = dict(count=count, page=page, mode='lite')
        if since_id:
            body['since_id'] = since_id
        resp = self.client.request('/statuses/mentions', 'GET', body)
        return json.loads(resp.read())

    def get_dm_list(self, count=20, page=1, since_id=None):
        body = dict(count=count, page=page, mode='lite')
        if since_id:
            body['since_id'] = since_id
        resp = self.client.request('/direct_messages/inbox', 'GET', body)
        return json.loads(resp.read())

    def send_msg(self, msg='test', user_id=None, user_name=None):
        user_name = user_name.encode('utf-8')
        user_id = user_id.encode('utf-8')
        if len(msg) > 140:
            num_msg_piece = int(math.ceil(len(msg) / 130.0))
            for piece in range(num_msg_piece):
                body = {
                    'status': '@%s\n(%d/%d) %s' % (
                        piece+1, num_msg_piece, user_name,
                        msg[130 * piece: 130 * piece + 130].encode('utf-8')
                    ),
                    'mode': 'lite'
                }
                self.client.request('/statuses/update', 'POST', body)
        else:
            body = {
                'status': '@%s\n%s' % (user_name, msg.encode('utf-8')),
                'mode': 'lite'
            }
            self.client.request('/statuses/update', 'POST', body)

    def send_dm(self, msg='test', user_id=None):
        user_id = user_id.encode('utf-8')
        if len(msg) > 140:
            num_msg_piece = int(math.ceil(len(msg) / 130.0))
            for piece in range(num_msg_piece):
                body = {
                    'user': user_id,
                    'text': '(%d/%d) %s' % (piece+1, num_msg_piece,
                            msg[130 * piece: 130 * piece + 130].encode('utf-8')
                    ),
                    'mode': 'lite'
                }
                self.client.request('/direct_messages/new', 'POST', body)
        else:
            body = {
                'user': user_id,
                'text': msg.encode('utf-8'),
                'mode': 'lite'
            }
            self.client.request('/direct_messages/new', 'POST', body)
    
    def delete_dm(self, dm_id):
        self.client.request('/direct_messages/destroy', 'POST', {'id': dm_id})

client = FanfouClient()
