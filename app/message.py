#! coding: utf-8
import fanfou
import json
import math

class FanfouClient:
    def __init__(self, consumer_token, access_token):
        self.client = fanfou.OAuth(consumer_token, access_token)

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

    # split message into pieces shorter than 140 characters
    def split_msg(self, msg, piece_len=130):
        assert(piece_len <= 140)
        if len(msg) <= piece_len:
            return [msg.encode('utf-8')]
        num_msg_piece = int(math.ceil(len(msg) * 1.0 / piece_len))
        msg_pieces = [
            msg[piece_len * p: piece_len * p + piece_len].encode('utf-8') for \
                    p in range(num_msg_piece)
        ]

        return msg_pieces

    def send_msg(self, msg='test', user_id=None, user_name=None):
        user_name = user_name.encode('utf-8')
        user_id = user_id.encode('utf-8')
        if len(msg) > 140:
            msg_pieces = self.split_msg(msg)
            for i, piece in enumerate(msg_pieces):
                body = {
                    'status': '@%s\n(%d/%d) %s' % (i+1, len(msg_pieces), piece),
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
            msg_pieces = self.split_msg(msg)
            for i, piece in enumerate(msg_pieces):
                body = {
                    'user': user_id,
                    'text': '(%d/%d) %s' % (i + 1, len(msg_pieces), piece),
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
