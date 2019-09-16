from datetime import datetime, timedelta

from knards import knards, api


def test_markers_arg_must_be_a_list_of_strings(init_db):
  """
  get_last_card() takes in an optional argument, markers, that must be a list
  of strings.
  """
  card_obj1 = knards.Card()
  api.create_card(card_obj1, init_db)

  result = api.get_last_card(markers=111, db_path=init_db)
  assert result is None

  result = api.get_last_card(markers='python', db_path=init_db)
  assert result is None

  result = api.get_last_card(markers=['python', 111], db_path=init_db)
  assert result is None

  result = api.get_last_card(markers=[], db_path=init_db)
  assert result.id == 1

def test_if_no_args_passed_in_method_returns_the_last_stored_card(init_db):
  """
  If no arguments are passed to the get_last_card() method, the method returns
  the card with the largest id from the set of cards with the most recent
  .date_created
  """
  card_obj1 = knards.Card(
    date_created=(datetime.today() - timedelta(1)).strftime('%Y-%m-%d'),
  )
  card_obj2 = knards.Card()
  card_obj3 = knards.Card()
  card_obj4 = knards.Card(
    date_created=(datetime.today() - timedelta(1)).strftime('%Y-%m-%d'),
  )
  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)
  api.create_card(card_obj4, init_db)

  result = api.get_last_card(db_path=init_db)
  assert result.id == 3

def test_method_returns_none_if_the_DB_is_empty_or_no_cards_found(init_db):
  """
  get_last_card() returns none if the DB is empty or, in case markers were
  passed to the method, no cards were found that contain all the specified
  markers.
  """
  result = api.get_last_card(db_path=init_db)
  assert result is None

  card_obj1 = knards.Card(markers='python specific')
  card_obj2 = knards.Card(markers='javascript specific')
  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)

  result = api.get_last_card(markers=['python', 'javascript'], db_path=init_db)
  assert result is None

def test_method_returns_a_proper_card_obj_upon_success(mocker, init_db):
  """
  get_last_card() returns an object of type knards.Card that is a copy of the
  last stored card object.
  If markers argument is passed to the method, it returns an object of type
  knards.Card that is a copy of the last stored card that has ALL of the
  specified markers.
  """
  card_obj1 = knards.Card(markers='python specific test')
  card_obj2 = knards.Card(markers='javascript specific')
  card_obj3 = knards.Card(
    markers='javascript specific test',
    date_created=(datetime.today() - timedelta(1)).strftime('%Y-%m-%d')
  )
  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)

  mocker.patch(
    'knards.api.get_card_set',
    return_value=api.get_card_set(db_path=init_db)
  )
  result = api.get_last_card(db_path=init_db)
  assert result.id == 2

  result = api.get_last_card(markers=['specific', 'test'], db_path=init_db)
  assert result.id == 1
