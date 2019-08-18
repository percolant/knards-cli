from datetime import datetime, date
import readchar
import sqlite3
import subprocess
import tempfile

from knards import knards, config, msg, util


def bootstrap_db(db_path=config.DB):
  """
  Creates the DB file and creates the "cards" table in it if there's no file
  with the name passed as the argument. Else returns False.
  """
  if type(db_path) is not str:
    print(msg.DB_PATH_MUST_BE_STR)
    return False

  # connection might fail here if the script has no permission to write to
  # db_path
  try:
    connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
  except sqlite3.OperationalError:
    print(msg.CANNOT_CONNECT_TO_DB_PERMISSION_DENIED.format(db_path))
    return False

  cursor = connection.cursor()

  # create the main "cards" table
  with connection:
    try:
      cursor.execute("""
        CREATE TABLE cards (
          id integer primary key,
          pos_in_series number,
          question text,
          answer text,
          markers text,
          series text,
          date_created date,
          date_updated date,
          score number
        )
      """)
    except sqlite3.OperationalError:
      print(msg.DB_ALREADY_EXISTS.format(db_path))
      return False

  print(msg.BOOTSTRAP_DB_SUCCESS.format(db_path))
  connection.close()
  return True

def get_card_set(
    revisable_only=False,
    show_question=True,
    show_answer=True,
    include_markers=[],
    exclude_markers=[],
    today=False
  ):
  """
  TODO
  """
  pass

def get_card_by_id(card_id, db_path=config.DB):
  """
  Takes in:
  1. An integer that represents target card's id.
  2. A path to the DB file (optional, defaults to config.DB)

  Returns an object of type knards.Card or None if a card with the given id
  wasn't found in the DB.
  """
  if type(card_id) is not int:
    print(msg.CARD_ID_MUST_BE_INT)
    return None

  connection = util.db_connect(db_path)
  if not connection:
    return None

  cursor = connection.cursor()

  with connection:
    cursor.execute("""
      SELECT * FROM cards WHERE id = {}
    """.format(card_id))
    card = cursor.fetchone()

  connection.close()

  if not card:
    return None

  card_obj = knards.Card(*card)
  return card_obj

def create_card(card_obj, db_path=config.DB):
  """
  Takes in:
  1. An object of type knards.Card
  2. A path to the DB file (optional, defaults to config.DB)

  Returns an id of the card in the DB created based on this object or None upon
  failure.
  """
  if type(card_obj) is not knards.Card:
    print(msg.INPUT_ARG_MUST_BE_CARD)
    return None

  connection = util.db_connect(db_path)
  if not connection:
    return None

  cursor = connection.cursor()

  # find a free id
  # this allows to reuse ids that were used and then freed up by deleting the
  # object
  free_id = 1
  with connection:
    cursor.execute("""
      SELECT (id) FROM cards
    """)

    for id in cursor.fetchall():
      if free_id != id[0]:
        break

      free_id += 1

    card_obj = card_obj._replace(id=free_id)

  created_with_id = None
  with connection:
    try:
      cursor.execute("""
        INSERT INTO cards VALUES ({})
      """.format(','.join(list('?' * len(card_obj)))), (card_obj))
      created_with_id = cursor.lastrowid
    except sqlite3.IntegrityError:
      print(msg.CANNOT_CREATE_CARD)

  connection.close()
  return created_with_id

def update_card(card_obj):
  """
  TODO
  """
  if type(card_obj) is not knards.Card:
    raise TypeError('Input arg must be of type Card')

  return True

def delete_card(card_id=None, markers=None, db_path=config.DB):
  """
  Deletes a card specified by id if id is passed as the argument.
  Deletes a set of cards that contain all markers sent as the 'markers'
  argument.
  Deletes a card specified by id if both 'card_id' and 'markers' args are
  passed in. Ignores 'markers'

  Third argument is a path to the DB file (optional, defaults to config.DB)

  Returns True upon success and False upon failure.
  """
  if card_id:
    if type(card_id) is not int:
      print(msg.CARD_ID_MUST_BE_INT)
      return False

  elif markers:
    if type(markers) is not str:
      print(msg.MARKERS_MUST_BE_STR)
      return False

  connection = util.db_connect(db_path)
  if not connection:
    return False

  cursor = connection.cursor()

  if card_id:
    with connection:
      cursor.execute("""
        DELETE FROM cards WHERE id = {}
      """.format(card_id))

  elif markers:
    pass

  connection.close()
  return True
