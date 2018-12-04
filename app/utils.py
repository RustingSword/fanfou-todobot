#!coding: utf-8
''' some utils '''
from dateutil.relativedelta import relativedelta
def htmlec(string):
    ''' convert escaped html to symbol '''
    escape_list = {'&lt;': '<', '&gt;': '>', '&quot;': '"', '&amp;': '&'}
    for escaped, original in escape_list.items():
        string = string.replace(escaped, original)
    return string

def format_task_list(tasks, brief=True):
    ''' build reply string from task list '''
    if tasks:
        return '\n'.join(
            ['%d) %s' % (i, t.brief_info() if brief else t.detail_info()) \
                        for (i, t) in tasks]
        )
    return u'没有任务'

def should_notify(now, scheduled):
    ''' minute level precision '''
    return ((now.year == scheduled.year)   and
            (now.month == scheduled.month) and
            (now.day == scheduled.day)     and
            (now.hour == scheduled.hour)   and
            (now.minute == scheduled.minute))

def next_notify_ts(last_notify_ts, notify_freq):
    ''' update notify time '''
    next_ts = last_notify_ts
    if notify_freq == 'once':  # don't notify again
        pass
    elif notify_freq == 'hourly':
        next_ts = last_notify_ts + relativedelta(hours=1)
    elif notify_freq == 'daily':
        next_ts = last_notify_ts + relativedelta(days=1)
    elif notify_freq == 'weekly':
        next_ts = last_notify_ts + relativedelta(weeks=1)
    elif notify_freq == 'monthly':
        next_ts = last_notify_ts + relativedelta(months=1)
    elif notify_freq == 'yearly':
        next_ts = last_notify_ts + relativedelta(years=1)
    return next_ts
