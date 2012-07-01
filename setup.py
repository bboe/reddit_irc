import os
import re
from setuptools import setup

NAME = 'reddit_irc'

HERE = os.path.abspath(os.path.dirname(__file__))
MODULE_FILE = os.path.join(HERE, '{0}.py'.format(NAME))
print MODULE_FILE
README = open(os.path.join(HERE, 'README.md')).read()
VERSION = re.search("__version__ = '([^']+)'",
                    open(MODULE_FILE).read()).group(1)


setup(name=NAME,
      version=VERSION,
      author='Bryce Boe',
      author_email='bbzbryce@gmail.com',
      url='https://github.com/bboe/reddit_irc',
      description='A tool to post new subreddit submissions to IRC channels.',
      long_description=README,
      keywords='reddit submission irc notification',
      classifiers=['Programming Language :: Python'],
      install_requires=['ircutils', 'praw'],
      py_modules=[NAME],
      entry_points={'console_scripts': ['{0} = {0}:main'.format(NAME)]})
