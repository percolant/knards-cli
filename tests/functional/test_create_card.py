from datetime import datetime, timedelta

from knards import knards, api


def test_input_arg_must_be_a_card_obj(init_db):
  """
  create_card() takes in only one argument and it must be of type knards.Card
  create_card() returns False upon failure.
  create_card() returns created card's id upon success.
  """
  result = api.create_card(111, init_db)
  assert result is False

  result = api.create_card('111', init_db)
  assert result is False

  card_obj = knards.Card()
  result = api.create_card(card_obj, init_db)
  assert result == 1

def test_create_card_return_valid_id(init_db):
  """
  api.create_card() takes in a knards.Card object, stores it in the DB and
  returns the id it was created with.
  """
  new_card = knards.Card()
  new_card_id = api.create_card(new_card, init_db)
  assert isinstance(new_card_id, int)

def test_create_card_index_generation(mocker, init_db):
  """
  Create multiple cards to test how new id are generated by the create_card()
  Also, it doesn't matter what ids do we explicitly assign to cards being
  passed to the method, those are being overwritten inside the method and this
  is expected behavior.
  """
  card_obj1 = knards.Card(id=1)
  card_obj2 = knards.Card(id=1)
  card_obj3 = knards.Card(id=1)

  card_id = api.create_card(card_obj1, init_db)
  assert card_id == 1

  card_id = api.create_card(card_obj2, init_db)
  assert card_id == 2

  card_id = api.create_card(card_obj3, init_db)
  assert card_id == 3

  # the removal of a card from the DB must free up its id and it should be
  # immediately available for new cards to take
  mocker.patch(
    'knards.api.get_card_by_id',
    return_value=api.get_card_by_id(card_id=2, db_path=init_db)
  )
  assert api.delete_card(card_id=2, db_path=init_db)
  card_id = api.create_card(card_obj1, init_db)
  assert card_id == 2
