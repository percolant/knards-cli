import os


HOME = os.environ.get('HOME', '')
EDITOR = 'vim'
# DB = HOME + '/.local/bin/knards.db'
DB = 'knards.db'

def get_DB_name():
  return DB
