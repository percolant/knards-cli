from datetime import datetime, date
from collections import abc
import sqlite3

from knards import knards, config, msg, util, exceptions


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
          date_created timestamp,
          date_updated timestamp,
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
    db_path=config.get_DB_name()
  ):
  """Outputs a set of objects of type knards.Card constrained by the passed in
  options

  Args:
    revisable_only (bool): Returns only card objects that are ready to be
  revised
    show_questions (bool): Include/exclude question text into results
    show_answer (bool): Include/exclude answer text into results
    include_markers (str[]): A list of markers all of which each card that is
  to be revised must have
    exclude_markers (str[]): A list of markers none of which each card that is
  to be revised must have
    today (bool): Returns only card objects that were already revised today
    db_path (str): The path to the DB (optional, defaults to what's defined in
      config module)

  Raises:
    TODO

  Returns:
    TODO
  """

  if not isinstance(revisable_only, bool):
    raise TypeError('revisable_only must be a boolean.')
  if not isinstance(today, bool):
    raise TypeError('today must be a boolean.')
  if not isinstance(show_question, bool):
    raise TypeError('show_question must be a boolean.')
  if not isinstance(show_answer, bool):
    raise TypeError('show_answer must be a boolean.')
  if not isinstance(include_markers, abc.Sequence):
    raise TypeError('include_markers must be a list.')
  if not isinstance(exclude_markers, abc.Sequence):
    raise TypeError('exclude_markers must be a list.')

  with util.db_connect(db_path) as connection:
    cursor = connection.cursor()
    cursor.execute("""
      SELECT * FROM cards
    """)
    card_set = cursor.fetchall()

  if not card_set:
    raise exceptions.EmptyDB('No cards adhere to the specified constraints.')

  # translate dates to str
  card_set_as_objects = []
  for card in card_set:
    card_set_as_objects.append(knards.Card(*list(card)))

  card_set_revisable = []
  for card in card_set_as_objects:
    # if revisable_only is True -> only return cards that has their score
    # equal to or more than the difference between today and the date of the
    # last card update (revision) and cards that weren't yet revised
    if revisable_only:
      if card.date_updated is None:
        card_set_revisable.append(card)
      elif card.score <= (
        datetime.now() - card.date_updated
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
      if card.date_updated and card.date_updated.date() == datetime.now().date():
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

def get_series_set(series_name, db_path=config.get_DB_name()):
  """Returns all cards that belong to the specified series.

  Args:
    series_name (str): The series name
    db_path (str): The path to the DB (optional, defaults to what's defined in
      config module)

  Raises:
    TODO

  Returns:
    A set of cards all of which belong to the series
  """

  if not isinstance(series_name, str):
    raise TypeError('\'series_name\' argument must be a list.')

  with util.db_connect(db_path) as connection:
    cursor = connection.cursor()
    cursor.execute("""
      SELECT * FROM cards WHERE series = '{}'
    """.format(series_name))
    card_set = cursor.fetchall()

  if not card_set:
    raise exceptions.EmptyDB('No cards adhere to the specified constraints.')

  sorted_card_set = {}
  for card in card_set:
    sorted_card_set[knards.Card(*card).pos_in_series] = knards.Card(*card)

  return sorted_card_set

def get_card_by_id(card_id, db_path=config.get_DB_name()):
  """
  Takes in:
  1. An integer that represents target card's id.
  2. A path to the DB file (optional, defaults to config.DB)

  Returns an object of type knards.Card representing the card data stored in
  the DB.
  """
  try:
    int(card_id)
  except ValueError:
    raise ValueError('id must be a proper number.')

  with util.db_connect(db_path) as connection:
    cursor = connection.cursor()
    cursor.execute("""
      SELECT * FROM cards WHERE id = {}
    """.format(card_id))
    card = cursor.fetchone()

  if not card:
    raise exceptions.CardNotFound(
      'Card #{} was not found in the DB.'.format(card_id)
    )

  card_obj = knards.Card(*card)
  card_obj = card_obj._replace(date_created=datetime.now())
  card_obj = card_obj._replace(score=0)

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
  if markers:
    if type(markers) is not list:
      print(msg.MARKERS_MUST_BE_LIST)
      return None
    else:
      for elem in markers:
        if type(elem) is not str:
          print(msg.MARKERS_MUST_BE_LIST)
          return None

  connection = util.db_connect(db_path)
  if not connection:
    return None

  cursor = connection.cursor()

  with connection:
    if not markers:
      cursor.execute("""
        SELECT * FROM cards WHERE id = (SELECT MAX(id) FROM cards WHERE \
date_created = (SELECT MAX(date_created) FROM cards))
      """)
      card = cursor.fetchone()
      if card:
        card_obj = knards.Card(*list(card))
    else:
      card_set = get_card_set()
      cards_to_pick_from = []

      # sift in only cards that contain all of the specified markers
      for card in card_set:
        has_markers = card.markers.split()
        for marker in markers:
          if marker not in has_markers:
            break
        else:
          cards_to_pick_from.append(card)

      if not cards_to_pick_from:
        print(msg.CARDS_BY_MARKERS_NOT_FOUND.format(', '.join(markers)))
        return None

      # find out the most recent date of addition of a card with specified markers
      max_date = datetime(1970, 1, 1)
      for card in cards_to_pick_from:
        if datetime.strptime(card.date_created, '%Y-%m-%d') > max_date:
          max_date = datetime.strptime(card.date_created, '%Y-%m-%d')
      max_date = max_date.strftime('%Y-%m-%d')

      # find out the max card id among the sifted in cards
      card_with_max_id = knards.Card(id=0)
      for card in cards_to_pick_from:
        if card.date_created == max_date and card.id > card_with_max_id.id:
          card_with_max_id = card

      card_obj = card_with_max_id
      card = 'This is a shitty algorithm, rewrite it!'

  connection.close()
  if not card:
    return None

  card_obj = card_obj._replace(date_created=datetime.now())
  card_obj = card_obj._replace(score=0)

  return card_obj

def create_card(card_obj, db_path=config.get_DB_name()):
  """
  Takes in:
  1. An object of type knards.Card
  2. A path to the DB file (optional, defaults to config.DB)

  Returns an id of the card in the DB created based on the passed in object.
  """
  if type(card_obj) is not knards.Card:
    raise ValueError('Input card object must be of type knards.Card')

  # find a free id
  # this allows to reuse ids that were used and then freed up by deleting the
  # object
  free_id = 1
  with util.db_connect(db_path) as connection:
    cursor = connection.cursor()
    cursor.execute("""
      SELECT (id) FROM cards
    """)

    for id in cursor.fetchall():
      if free_id != id[0]:
        break

      free_id += 1

    card_obj = card_obj._replace(id=free_id)

  with util.db_connect(db_path) as connection:
    cursor = connection.cursor()
    cursor.execute("""
      INSERT INTO cards VALUES ({})
    """.format(','.join(list('?' * len(card_obj)))), (card_obj))
    created_with_id = cursor.lastrowid

  return created_with_id

def update_card(card_obj, db_path=config.get_DB_name()):
  """
  Takes in:
  1. An object of type knards.Card
  2. A path to the DB file (optional, defaults to config.DB)

  Returns the id of the card that is updated.
  """
  if type(card_obj) is not knards.Card:
    raise ValueError('Input card object must be of type knards.Card')

  with util.db_connect(db_path) as connection:
    cursor = connection.cursor()
    cursor.execute("""
      UPDATE cards SET question = ?,
                       answer = ?,
                       markers = ?,
                       series = ?,
                       pos_in_series = ?,
                       date_updated = ?,
                       score = ?
                   WHERE id = ?
    """, (
      card_obj.question,
      card_obj.answer,
      card_obj.markers,
      card_obj.series,
      card_obj.pos_in_series,
      datetime.now(),
      card_obj.score,
      card_obj.id
    ))

  return card_obj.id

def delete_card(card_id=None, markers=None, db_path=config.get_DB_name()):
  """Deletes a card/cards from the DB

  Args:
    card_id (int): The id of the card that is to be deleted
    markers (str[]): A list of markers all of which each card that is to be
      deleted must have
    db_path (str): The path to the DB (optional, defaults to what's defined in
      config module)

  Raises:
    TODO

  Returns:
    card_id: id of the card that was deleted
    deleted_ids: List of all deleted cards' ids
  """

  assert card_id or markers
  assert isinstance(db_path, str) and len(db_path) > 0

  if card_id:
    if not isinstance(get_card_by_id(card_id), knards.Card):
      raise exceptions.CardNotFound(
        'Card #{} does not exist in the DB.'.format(card_id)
      )

    with util.db_connect(db_path) as connection:
      cursor = connection.cursor()
      cursor.execute("""
        DELETE FROM cards WHERE id = {}
      """.format(card_id))

    return card_id

  elif markers:
    if not isinstance(markers, list):
      raise TypeError('\'markers\' argument must be a list.')

    card_set = get_card_set(include_markers=markers)
    assert len(card_set) != len(get_card_set())

    with util.db_connect(db_path) as connection:
      cursor = connection.cursor()
      for card in card_set:
        cursor.execute("""
          DELETE FROM cards WHERE id = {}
        """.format(card.id))

    return [card.id for card in card_set]
