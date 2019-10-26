import os


HOME = os.environ.get('HOME', '')
EDITOR = 'vim'
# DB = HOME + '/.local/bin/knards.db'
DB = 'knards.db'
TMP_PATH = '/tmp/knards_backups/'

def get_DB_name():
  return DB

def get_tmp_path():
  return TMP_PATH
