from knards import knards, api


def test_get_card_by_id_returns_object_of_proper_type_and_has_id_set(init_db):
  """
  get_card_by_id() is expected to return an object of type knards.Card with
  the proper id set (one it was stored with)
  """
  card_obj = knards.Card()
  card_id = api.create_card(card_obj, init_db)
  return_value = api.get_card_by_id(card_id, init_db)

  assert isinstance(return_value, knards.Card)
  assert return_value.id == card_id

def test_get_card_by_id_with_nonexistent_id(init_db):
  """
  get_card_by_id() returns None if a card with the passed in id wasn't found
  in the DB.
  """
  return_value = api.get_card_by_id(1, init_db)
  assert return_value is None
