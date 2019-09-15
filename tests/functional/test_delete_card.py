from datetime import datetime, timedelta

from knards import knards, api


def test_card_id_arg_must_be_a_number(mocker, init_db):
  """
  One of the arguments delete_card() takes in is card_id, which must be a
  proper integer number.
  """
  card_obj = knards.Card()
  card_id = api.create_card(card_obj, init_db)
  assert card_id == 1

  mocker.patch(
    'knards.api.get_card_by_id',
    return_value=api.get_card_by_id(card_id, init_db)
  )

  result = api.delete_card(card_id='1', db_path=init_db)
  assert result is False

  result = api.delete_card(card_id=1, db_path=init_db)
  assert result is True

def test_markers_arg_must_be_a_list_of_strings(init_db):
  """
  One of the arguments delete_card() takes in is markers, which must be a list
  of strings.
  """
  card_obj = knards.Card()
  api.create_card(card_obj, init_db)

  result = api.delete_card(markers='python', db_path=init_db)
  assert result is False

  result = api.delete_card(markers=1, db_path=init_db)
  assert result is False

  result = api.delete_card(markers=[1, 2, 3], db_path=init_db)
  assert result is False

  result = api.delete_card(markers=['python'], db_path=init_db)
  assert result is True

def test_if_card_id_is_passed_in_method_deletes_the_card_with_that_id(
  mocker,
  init_db
):
  """
  If card_id argument is passed to the delete_card() method, the card with
  that id is removed from the DB.
  """
  card_obj = knards.Card()
  card_id = api.create_card(card_obj, init_db)

  result = api.get_card_by_id(card_id, init_db)
  assert result.id == card_id

  mocker.patch(
    'knards.api.get_card_by_id',
    return_value=api.get_card_by_id(card_id, init_db)
  )
  api.delete_card(card_id=card_id, db_path=init_db)
  mocker.stopall()

  result = api.get_card_by_id(card_id, init_db)
  assert result is None

def test_if_card_id_is_passed_in_and_card_doesnt_exist_method_returns_false(
  mocker,
  init_db
):
  """
  If card_id argument is passed to the delete_card() method and the respective
  card doesn't exist in the DB, method returns False and nothing is removed
  from the DB.
  """
  mocker.patch(
    'knards.api.get_card_by_id',
    return_value=api.get_card_by_id(1, init_db)
  )
  result = api.delete_card(card_id=1, db_path=init_db)
  assert result is False

def test_if_markers_passed_in_all_cards_with_those_markers_are_removed(
  mocker,
  init_db
):
  """
  If markers list is passed to the delete_card() method, all cards that contain
  ALL of the specified markers are being removed from the DB.
  """
  card_obj1 = knards.Card(markers='python specific')
  card_obj2 = knards.Card(markers='python nonspecific')
  card_obj3 = knards.Card(markers='javascript specific test')
  card_obj4 = knards.Card(markers='python special')
  card_obj5 = knards.Card(markers='python specific test')
  card_obj6 = knards.Card(markers='specifically test')
  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)
  api.create_card(card_obj4, init_db)
  api.create_card(card_obj5, init_db)
  api.create_card(card_obj6, init_db)

  assert len(api.get_card_set(db_path=init_db)) == 6

  mocker.patch(
    'knards.api.get_card_set',
    return_value=api.get_card_set(db_path=init_db)
  )
  assert api.delete_card(markers=['specific', 'test'], db_path=init_db) is True
  mocker.stopall()

  assert len(api.get_card_set(db_path=init_db)) == 4

def test_if_markers_passed_in_method_returns_true_always(mocker, init_db):
  """
  If no cards contain the specified set of markers, no cards are removed from
  the DB and True is returned.
  """
  card_obj1 = knards.Card(markers='python specific')
  card_obj2 = knards.Card(markers='python nonspecific')
  card_obj3 = knards.Card(markers='javascript specific')
  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)

  assert len(api.get_card_set(db_path=init_db)) == 3

  mocker.patch(
    'knards.api.get_card_set',
    return_value=api.get_card_set(db_path=init_db)
  )
  assert api.delete_card(markers=['specific', 'test'], db_path=init_db) is True
  mocker.stopall()

  assert len(api.get_card_set(db_path=init_db)) == 3

def test_if_card_id_and_markers_are_passed_in_markers_are_ignored(
  mocker,
  init_db
):
  """
  If both card_id and markers are passed to the delete_card() method, markers
  are ignored and only the card with the card_id id is removed from the DB.
  """
  card_obj1 = knards.Card(markers='python specific')
  card_obj2 = knards.Card(markers='python nonspecific')
  card_obj3 = knards.Card(markers='javascript specific')
  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)

  assert len(api.get_card_set(db_path=init_db)) == 3

  mocker.patch(
    'knards.api.get_card_by_id',
    return_value=api.get_card_by_id(1, db_path=init_db)
  )
  mocker.patch(
    'knards.api.get_card_set',
    return_value=api.get_card_set(db_path=init_db)
  )
  assert api.delete_card(
    card_id=4,
    markers=['specific'],
    db_path=init_db
  ) is True
  mocker.stopall()

  assert len(api.get_card_set(db_path=init_db)) == 3

  mocker.patch(
    'knards.api.get_card_by_id',
    return_value=api.get_card_by_id(1, db_path=init_db)
  )
  mocker.patch(
    'knards.api.get_card_set',
    return_value=api.get_card_set(db_path=init_db)
  )
  assert api.delete_card(
    card_id=1,
    markers=['specific'],
    db_path=init_db
  ) is True
  mocker.stopall()

  assert len(api.get_card_set(db_path=init_db)) == 2
