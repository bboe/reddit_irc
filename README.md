reddit_irc is an IRC bot that can be configured to notify various channels of
new submissions to various subreddit communities.

## Example reddit_irc.ini file

```
[DEFAULT]
irc_port: 6667
irc_ssl: false
reddit_agent: YOUR AGENT STRING

[freenode]
irc_name: USERNAME
irc_pswd: PASSWORD
irc_host: chat.freenode.net
irc_port: 7000
irc_ssl: true
mapping: #channel1:subreddit1+subreddit2,#channel2:another_subreddit

[rizon]
irc_name: USERNAME
irc_pswd: PASSWORD
irc_host: irc.rizon.net
irc_port: 9999
irc_ssl: true
mapping: #some_channel:some_subreddit
```
