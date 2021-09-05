import os


HOME = os.environ.get('HOME', '')
EDITOR = 'vim'
DB = HOME + '/.local/bin/knards.db'
# DB = 'knards.db'
BACKUP_PATH = HOME + '/.local/bin/knards_backups/'
# BACKUP_PATH = './knards_backups/'
TAGS_GROUP_1 = [
    'türkçe',
    'english',
    'deutsch',
    'čeština',
    'français',
    'español',
    'italiano',
    'magyar',
    'português',
    'azərbaycanca'
]
TAGS_GROUP_2 = [
    'Roman',
    'Greece',
    'East',
    'Czech',
    'Britain',
    'Ukraine',
    'World'
]
TAGS_GROUP_3 = [
    'python',
    'JavaScript',
    'Angular',
    'Django',
    # 'docker',
    # 'ansible',
    'TypeScript',
    # 'SQL',
    # 'CSS',
    # 'git',
    # 'TDD',
    'linux',
    'React',
    # 'flask',
    # 'nodejs',
    'aiohttp',
    # 'PostgreSQL',
]
TAGS_GROUP_4 = [
    'quotes',
    'music',
    'health',
    'maths',
    'chess'
]
TAGS_LIST = {
    'languages': TAGS_GROUP_1,
    'history': TAGS_GROUP_2,
    'IT': TAGS_GROUP_3,
    'misc': TAGS_GROUP_4,
}
TAGS_ONLY_REVISE = [
    'russian',
    'čeština',
    'english',
    'quotes',
    'music',
    'health',
    'maths',
    'chess',
    'git'
]

def get_DB_name():
    return DB

def get_backup_path():
    return BACKUP_PATH

def get_tags_list():
    return TAGS_LIST

def get_tags_only_revise_list():
    return TAGS_ONLY_REVISE
