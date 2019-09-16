from knards import knards, api


def test_card_id_input_arg_must_be_integer(init_db):
  """
  get_card_by_id() takes in a card_id input argument, that must be integer.
  """
  card_obj = knards.Card()
  card_id = api.create_card(card_obj, init_db)

  result = api.get_card_by_id('1', init_db)
  assert result is None

def test_returns_object_of_proper_type_and_has_id_set(init_db):
  """
  get_card_by_id() is expected to return an object of type knards.Card with
  the proper id set (one it was stored with)
  """
  card_obj = knards.Card()
  card_id = api.create_card(card_obj, init_db)
  result = api.get_card_by_id(card_id, init_db)

  assert isinstance(result, knards.Card)
  assert result.id == card_id

def test_if_nonexistent_id_passed_in_none_is_returned(init_db):
  """
  get_card_by_id() returns None if a card with the passed in id wasn't found
  in the DB.
  """
  result = api.get_card_by_id(1, init_db)
  assert result is None
