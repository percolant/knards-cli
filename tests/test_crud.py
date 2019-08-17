import pytest
from knards import knards, api


def test_create_card_return_valid_id():
  """
  create_card methods takes in a Card object, stores it in the DB and returns
  its id
  """
  new_card = knards.Card()
  new_card_id = api.create_card(new_card)
  assert isinstance(new_card_id, int)

def test_get_card_by_id_returns_object_of_proper_type_and_has_id_set():
  """
  get_card_by_id is expected to return an object of type knards.Card
  """
  card_obj = knards.Card()
  card_id = api.create_card(card_obj)
  return_value = api.get_card_by_id(card_id)

  assert isinstance(return_value, knards.Card)
  assert return_value.id == card_id
