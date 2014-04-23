#!/usr/bin/env python
import asyncore
import re
import praw
import sys
import time
from ircutils import bot
from six import text_type
from six.moves import configparser

debug = True

__version__ = '0.1.3'


class RedditBot(bot.SimpleBot):
    MSG_FORMAT = u'{shortlink} New post to /r/{subreddit} by {author}: {title}'
    IGNORE_EVENTS = set(('CONN_CONNECT', 'CTCP_VERSION', 'JOIN', 'KICK',
                         'MODE', 'NICK', 'PART', 'PING', 'PRIVMSG', 'QUIT',
                         'RPL_BOUNCE', 'RPL_CREATED', 'RPL_ENDOFMOTD',
                         'RPL_ENDOFNAMES', 'RPL_GLOBALUSERS', 'RPL_LOCALUSERS',
                         'RPL_LUSERCHANNELS', 'RPL_LUSERCLIENT', 'RPL_LUSERME',
                         'RPL_LUSEROP', 'RPL_LUSERUNKNOWN', 'RPL_MOTD',
                         'RPL_MOTDSTART', 'RPL_MYINFO', 'RPL_NAMREPLY',
                         'RPL_STATSCONN', 'RPL_TOPIC', 'RPL_TOPICWHOTIME',
                         'RPL_YOURHOST', 'RPL_YOURID', 'RPL_WELCOME', 'TOPIC'))

    def __init__(self, nick, server):
        bot.SimpleBot.__init__(self, nick)
        self.real_name = '%s (https://github.com/bboe/reddit_irc)' % nick
        self.server = server

    def on_any(self, event):
        if event.command in self.IGNORE_EVENTS:
            return
        print('\t%r %s (%s->%s) %s' % (self.server, event.command,
                                       event.source, event.target,
                                       event.params))

    def on_channel_message(self, event):
        sys.stderr.write('%r (%s) <%s> %s\n' %
                         (self.server, event.target, event.source,
                          event.message))
        sys.stderr.flush()

    def on_private_message(self, event):
        print('(PRIVATE %r) <%s> %s' % (self.server, event.source,
                                        event.message))

    def announce(self, submission, channel):
        msg = self.MSG_FORMAT.format(
            url=submission.url,
            permalink=submission.permalink,
            shortlink=submission.short_link,
            subreddit=text_type(submission.subreddit),
            author=text_type(submission.author),
            title=submission.title).encode('utf-8')
        msg = re.sub('\s+', ' ', msg).strip()
        if debug:
            print(msg)
        self.send_message(channel, msg)


class RedditUpdater(object):
    MSG_LIMIT = 3
    class_reddit = None

    def __init__(self, subreddit):
        self.sr_name = subreddit
        self.subreddit = self.class_reddit.get_subreddit(subreddit)
        self.previous = self.subreddit.get_new().next()
        self.associations = []
        if debug:
            print('Added %s' % subreddit)
            print('\tLast submission: %r' % self.previous.title)

    def add(self, server_bot, channel):
        self.associations.append((server_bot, channel))

    def update(self):
        submissions = []
        try:
            for submission in self.subreddit.get_new():
                if submission.created_utc <= self.previous.created_utc:
                    break
                submissions.append(submission)
        except Exception as error:
            print(text_type(error))
            return
        if not submissions:
            return
        if len(submissions) > self.MSG_LIMIT:
            submissions = submissions[-self.MSG_LIMIT:]
        self.previous = submissions[0]
        for submission in reversed(submissions):
            for server_bot, channel in self.associations:
                server_bot.announce(submission, channel)


class Runner(object):
    CHECK_TIME = 30

    def __init__(self):
        self.bots = {}
        self.reddits = {}
        self.load_configuration()

    def load_configuration(self):
        config = configparser.RawConfigParser()
        if not config.read(['reddit_irc.ini']):
            raise Exception('Could not find settings file.')
        RedditUpdater.class_reddit = praw.Reddit(config.get('DEFAULT',
                                                            'reddit_agent'))
        if config.has_option('DEFAULT', 'check_time'):
            self.CHECK_TIME = int(config.get('DEFAULT', 'check_time'))
        for server in config.sections():
            self.parse_server(server, dict(config.items(server)))

    def parse_server(self, server, items):
        mappings = re.sub('\s', '', items['mapping']).split(',')
        if not mappings:
            raise Exception('No mappings for %r' % server)
        bot = RedditBot(items['irc_name'], server)
        self.bots[server] = bot
        channels = []
        for mapping in mappings:
            channel, subs = mapping.split(':', 1)
            norm_subs = '+'.join(sorted(subs.split('+')))
            if not norm_subs:
                raise Exception('No subreddits for %r:%r' % (server, channel))
            channels.append(channel)
            if norm_subs not in self.reddits:
                self.reddits[norm_subs] = RedditUpdater(norm_subs)
            self.reddits[norm_subs].add(bot, channel)
        use_ssl = items['irc_ssl'].lower() in ('1', 'yes', 'true', 'on')
        bot.connect(items['irc_host'], int(items['irc_port']),
                    channel=channels,
                    use_ssl=use_ssl)
        if 'irc_msg' in items:
            bot.MSG_FORMAT = text_type(items['irc_msg'])
        if 'irc_pswd' in items:
            bot.identify(items['irc_pswd'])

    def run(self):
        now = time.time()
        check_time = now + self.CHECK_TIME
        while True:
            wait_time = check_time - now
            asyncore.loop(timeout=wait_time, count=1)
            now = time.time()
            if now >= check_time:
                for reddit in self.reddits.values():
                    reddit.update()
                check_time = now + self.CHECK_TIME


def main():
    runner = Runner()
    runner.run()


if __name__ == '__main__':
    sys.exit(main())
