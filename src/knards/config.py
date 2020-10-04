import os


HOME = os.environ.get('HOME', '')
EDITOR = 'vim'
# DB = HOME + '/.local/bin/knards.db'
DB = 'knards.db'
# BACKUP_PATH = HOME + '/.local/bin/knards_backups/'
BACKUP_PATH = './knards_backups/'
TAGS_GROUP_1 = [
    'first',
    'second',
    'third'
]
TAGS_GROUP_2 = [
    'first',
    'second',
    'third'
]
TAGS_LIST = {
    'first': TAGS_GROUP_1,
    'second': TAGS_GROUP_2
}

def get_DB_name():
    return DB

def get_backup_path():
    return BACKUP_PATH

def get_tags_list():
    return TAGS_LIST
