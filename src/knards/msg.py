# AUXILIARY TEXTS
DIVIDER_LINE = '--------------------------------------------------------------\
--------------------------------------'
CARD_LIST_TEMPLATE = '=== #{} | {} | #{} in "{}" | {} | {} | {} ===\n'

# SUCCESS MESSAGES
BOOTSTRAP_DB_SUCCESS = '{} was successfully created.'
NEW_CARD_SUCCESS = 'Card #{} was successfully created.'
EDIT_CARD_SUCCESS = 'Card #{} was successfully updated.'

# FAILURE MESSAGES
DB_ALREADY_EXISTS = '{} already exists!'
DB_PATH_MUST_BE_STR = 'db_path input arg must of type str'
CANNOT_CREATE_CARD = 'Could not store the card in the DB due to an error.'
CANNOT_CREATE_DB = '{} already exists, remove it first (or change the name of \
DB in config.py), then run this command again.'
CANNOT_CONNECT_TO_DB_PERMISSION_DENIED = 'Permission denied while trying to \
access {}'
CANNOT_CONNECT_TO_DB_NO_DB = 'cards table wasn\'t found in {}. First, \
initialize the DB via bootstrap-db command.'
CARD_ID_MUST_BE_INT = 'Card\'s id must be an integer number.'
MARKERS_MUST_BE_LIST = 'Markers must be a list of strings.'
INPUT_ARG_MUST_BE_CARD = 'Input argument must be an object of type knards.Card'
NEW_CARD_FAILURE = 'Couldn\'t save the card to the DB. Make sure the file \
with it does exist.'
EDIT_CARD_FAILURE = 'Couldn\'t save the card to the DB.'
CARD_BY_ID_NOT_FOUND = 'Card #{} doesn\'t exist in the DB.'
CARDS_BY_MARKERS_NOT_FOUND = 'No cards containing markers "{}" has been found \
in the DB.'

RETRY = 'Retry? (press \'y\' to retry or any other key to abort)'
CLI_ERROR_DONT_CHANGE_MARKERS = 'Don\'t change the structure of the prompt \
file - first line must look like this: Markers: [here type in markers for the \
card]'
CLI_ERROR_DONT_CHANGE_SERIES = 'Don\'t change the structure of the prompt \
file - second line must look like this: Series: [here, type in the name for \
the series of which this card will be part of]'
CLI_ERROR_DONT_CHANGE_POS_IN_SERIES = 'Don\'t change the structure of the \
prompt file - third line must look like this: No. in series: positional \
number within the same series'
CLI_ERROR_DONT_CHANGE_DIVIDER_LINE = 'Don\'t change the structure of the \
prompt file - fourth line must be the divider line between card\'s metadata \
and the content.'
CLI_ERROR_TOO_MANY_DIVIDER_LINES = 'Don\'t add additional divider lines to \
the prompt file.'
