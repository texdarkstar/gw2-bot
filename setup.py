try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


config = {
    'description': 'Bot class for dirty cheating (:P) python robots',
    'author': 'MTA Jr.',
    'url': 'http://github.com/texdarkstar/gw2-bot',
    'download_url': 'http://github.com/texdarkstar/gw2-bot/archive/master.zip',
    'author_email': 'texdarkstar@fastmail.fm',
    'version': '1.0',
    'scripts': ['bot.py'],
    'name': 'gw2-bot'
}

setup(**config)
