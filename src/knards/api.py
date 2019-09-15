from datetime import datetime, date
import sqlite3

from knards import knards, config, msg, util


def bootstrap_db(db_path=config.DB):
  """
  Creates the DB file and creates the "cards" table in it if there's no file
  with the name passed as the argument. Otherwise returns False.
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
    today=False,
    db_path=config.DB
  ):
  """
  Takes in:
  1. revisable_only - only output cards that are ready to be revised (see below)
  2. show_question - include/exclude the question text from returned card objects.
  3. show_answer - include/exclude the answer text from returned card objects.
  4. include_markers - must be list -> markers that MUST be present in each
  returned card.
  5. exclude_markers - must be list -> markers that any one of the returned
  cards may have.
  6. today - only output cards that were already revised today.

  Outputs a list of objects of type knards.Card or [] upon failure.
  """
  if not isinstance(revisable_only, bool) or \
    not isinstance(today, bool) or \
    not isinstance(show_question, bool) or \
    not isinstance(show_answer, bool) or \
    not isinstance(include_markers, list) or \
    not isinstance(exclude_markers, list):
    return []

  connection = util.db_connect(db_path)
  if not connection:
    return []

  cursor = connection.cursor()

  with connection:
    cursor.execute("""
      SELECT * FROM cards
    """)
    card_set = cursor.fetchall()

  connection.close()

  if not card_set:
    return []

  # translate dates to str
  card_set_as_objects = []
  for card in card_set:
    holder = list(card)
    for index, prop in enumerate(holder):
      if isinstance(prop, date):
        holder[index] = prop.strftime('%Y-%m-%d')
    # and cast to knards.Card
    card_set_as_objects.append(knards.Card(*holder))

  card_set_revisable = []
  for card in card_set_as_objects:
    # if revisable_only is True -> only return cards that has their score
    # equal to or more than the difference between today and the date of the
    # last card update (revision) and cards that weren't yet revised
    if revisable_only:
      if card.date_updated is None:
        card_set_revisable.append(card)
      elif card.score <= (
        datetime.today() - datetime.strptime(card.date_updated, '%Y-%m-%d')
      ).days:
        card_set_revisable.append(card)
    else:
      card_set_revisable = card_set_as_objects
      break

  card_set_included_markers = []
  for card in card_set_revisable:
    # if include_markers is not '' -> filter cards that must have all of the
    # specified markers (as whole words)
    if include_markers:
      compare_list = card.markers.split()
      for marker in include_markers:
        if not marker in compare_list:
          break
      else:
        card_set_included_markers.append(card)
    else:
      card_set_included_markers = card_set_revisable
      break

  card_set_excluded_markers = []
  for card in card_set_included_markers:
    # if exclude_markers is not '' -> filter cards that must have none of the
    # specified markers (as whole words)
    if exclude_markers:
      compare_list = card.markers.split()
      for marker in exclude_markers:
        if marker in compare_list:
          break
      else:
        card_set_excluded_markers.append(card)
    else:
      card_set_excluded_markers = card_set_included_markers
      break

  card_set_today = []
  for card in card_set_excluded_markers:
    # return cards that have date_updated equal to today's date (were revised
    # today)
    if today:
      if card.date_updated == datetime.today().strftime('%Y-%m-%d'):
        card_set_today.append(card)
    else:
      card_set_today = card_set_excluded_markers
      break

  if not show_question:
    card_set_without_questions = []
    for card in card_set_today:
      card_set_without_questions.append(card._replace(question=''))
  else:
    card_set_without_questions = card_set_today

  if not show_answer:
    card_set_without_answers = []
    for card in card_set_without_questions:
      card_set_without_answers.append(card._replace(answer=''))
  else:
    card_set_without_answers = card_set_without_questions

  return card_set_without_answers

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

  # cast card to list, translate dates to str
  card = list(card)
  for index, prop in enumerate(card):
    if isinstance(prop, date):
      card[index] = prop

  card_obj = knards.Card(*card)
  return card_obj

def get_last_card(markers=None, db_path=config.DB):
  """
  Takes in:
  1. A list of strings that represent the set of markers that all the affected
  card objects must contain.
  2. A path to the DB file (optional, defaults to config.DB)

  If 'markers' is not passed in, returns a knards.Card object that's a copy of
  the most recently created card. If 'markers' is passed in, returns a
  knards.Card object that's a copy of the most recently created card that
  contains ALL of the specified markers.

  Returns None upon if the DB is empty or if no cards contain all of the
  specified markers (if 'markers' were passed in)
  """
  connection = util.db_connect(db_path)
  if not connection:
    return None

  cursor = connection.cursor()

  with connection:
    cursor.execute("""
      SELECT * FROM cards WHERE id = (SELECT MAX(id) FROM cards WHERE date_created = (SELECT MAX(date_created) FROM cards))
    """)
    card_obj = knards.Card(*list(cursor.fetchone()))

  connection.close()
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

def update_card(card_obj, db_path=config.DB):
  """
  Takes in:
  1. An object of type knards.Card
  2. A path to the DB file (optional, defaults to config.DB)

  Returns True upon success and False upon failure.
  """
  if type(card_obj) is not knards.Card:
    raise TypeError('Input arg must be of type Card')

  return True

def delete_card(card_id=None, markers=None, db_path=config.DB):
  """
  Takes in:
  1. An integer number representing an id of an existing card object.
  2. A list of strings representing a set of markers that all the affected card
  objects must contain.
  3. A path to the DB file (optional, defaults to config.DB)

  Deletes a card specified by card_id.
  Deletes a set of cards that contain ALL markers sent as the 'markers'
  argument.
  Deletes a card specified by id if both 'card_id' and 'markers' args are
  passed in. Ignores 'markers'

  Returns True upon success and False upon failure.
  """
  if card_id:
    if type(card_id) is not int:
      print(msg.CARD_ID_MUST_BE_INT)
      return False

    if not get_card_by_id(card_id):
      print(msg.CARD_BY_ID_NOT_FOUND.format(card_id))
      return False

  elif markers:
    if type(markers) is not list:
      print(msg.MARKERS_MUST_BE_LIST)
      return False
    else:
      for elem in markers:
        if type(elem) is not str:
          print(msg.MARKERS_MUST_BE_LIST)
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
    ids_to_delete = []

    card_set = get_card_set()

    for card in card_set:
      has_markers = card.markers.split()
      for marker in markers:
        if marker not in has_markers:
          break
      else:
        ids_to_delete.append(card.id)

    for id in ids_to_delete:
      with connection:
        cursor.execute("""
          DELETE FROM cards WHERE id = {}
        """.format(id))

  connection.close()
  return True
