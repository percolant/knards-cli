import os


HOME = os.environ.get('HOME', '')
EDITOR = 'vim'
# DB = HOME + '/.local/bin/knards.db'
DB = 'knards.db'
BACKUP_PATH = HOME + '/.local/bin/knards_backups/'

def get_DB_name():
  return DB

def get_backup_path():
  return BACKUP_PATH
