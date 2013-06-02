import os
import re
from setuptools import setup

MODULE_NAME = 'reddit_irc'

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
VERSION = re.search("__version__ = '([^']+)'",
                    open('{0}.py'.format(MODULE_NAME)).read()).group(1)

setup(name=MODULE_NAME,
      author='Bryce Boe',
      author_email='bbzbryce@gmail.com',
      classifiers=['License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      entry_points={'console_scripts': ['{0} = {0}:main'.format(MODULE_NAME)]},
      description='A tool to post new subreddit submissions to IRC channels.',
      install_requires=['ircutils', 'praw>=2.0.11'],
      keywords='reddit submission irc notification',
      license='Simplified BSD License',
      long_description=README,
      py_modules=[MODULE_NAME],
      url='https://github.com/bboe/reddit_irc',
      version=VERSION)
