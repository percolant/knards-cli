# AUXILIARY TEXTS
DIVIDER_LINE = '--------------------------------------------------------------\
--------------------------------------'

# SUCCESS MESSAGES
BOOTSTRAP_DB_SUCCESS = '{} was successfully created.'

# FAILURE MESSAGES
DB_ALREADY_EXISTS = '{} already exists!'
CANNOT_CREATE_CARD = 'Could not store the card in the DB due to an error.'
CANNOT_CREATE_DB = '{} already exists, remove it first (or change the name of \
DB in config.py), then run this command again.'
CANNOT_CONNECT_TO_DB_PERMISSION_DENIED = 'Permission denied while trying to \
access {}'
CANNOT_CONNECT_TO_DB_NO_DB = 'cards table wasn\'t found in {}. First, \
initialize the DB via bootstrap-db command.'
CARD_ID_MUST_BE_INT = 'Card\'s id must be an integer number.'
MARKERS_MUST_BE_STR = 'Markers must be a string.'
INPUT_ARG_MUST_BE_CARD = 'Input argument must be an object of type knards.Card'
