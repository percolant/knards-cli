from datetime import datetime, date
import readchar
import sqlite3
import subprocess
import tempfile

from knards import knards, config, msg


def bootstrap_db(db_name):
  """
  TODO
  """
  if type(db_name) is not str:
    raise TypeError('Input arg must be of type str')

  connection = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
  cursor = connection.cursor()

  # creating the main "cards" table
  with connection:
    try:
      cursor.execute("""
        SELECT * FROM cards
      """)
      print(msg.CANNOT_CREATE_DB.format(db_name))
    except sqlite3.OperationalError:
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

def get_card_by_id(card_id):
  """
  Takes in an integer that represents target card's id.
  Returns an object of type knards.Card
  """
  if type(card_id) is not int:
    raise TypeError('Target card\'s id must be an integer number')

  connection = sqlite3.connect(config.DB, detect_types=sqlite3.PARSE_DECLTYPES)
  cursor = connection.cursor()

  with connection:
    cursor.execute("""
      SELECT * FROM cards WHERE id = {}
    """.format(card_id))
    card = cursor.fetchone()

  connection.close()
  card_obj = knards.Card(*card)
  return card_obj

def create_card(card_obj):
  """
  TODO
  """
  if type(card_obj) is not knards.Card:
    raise TypeError('Input arg must be of type Card')

  connection = sqlite3.connect(config.DB, detect_types=sqlite3.PARSE_DECLTYPES)
  cursor = connection.cursor()

  # get the next free id
  with connection:
    try:
      cursor.execute("""
        SELECT MAX(id) FROM cards
      """)
      card_obj = card_obj._replace(id=(cursor.fetchone()[0] or 0) + 1)
    except sqlite3.DatabaseError:
      print(msg.CANNOT_CREATE_CARD)
      return False

  with connection:
    try:
      cursor.execute("""
        INSERT INTO cards VALUES ({})
      """.format(','.join(list('?' * len(card_obj)))), (card_obj))
    except sqlite3.DatabaseError:
      print(msg.CANNOT_CREATE_CARD)
      return False

  connection.close()

  return card_obj.id

def update_card(card_obj):
  """
  TODO
  """
  if type(card_obj) is not knards.Card:
    raise TypeError('Input arg must be of type Card')

  return True

def delete_card(card_id=None, marker=None):
  """
  TODO
  """
  if card_id:
    if type(card_id) is not int:
      raise TypeError('Target card\'s id must be an integer number')
  elif marker:
    if type(marker) is not str:
      raise TypeError('Markers list must be a string')

  if card_id or marker:
    pass

  return True
