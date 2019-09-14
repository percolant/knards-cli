from datetime import datetime

from knards import knards, api


def test_fail_if_input_arg_is_not_a_proper_card_object(init_db):
  """
  update_card() takes in only one argument and it must be of type knards.Card
  update_card() always returns a boolean value.
  """
  card_obj = knards.Card()
  card_id = api.create_card(card_obj, init_db)

  result = api.update_card(111, init_db)
  assert result == False

  result = api.update_card('not a card', init_db)
  assert result == False

  result = api.update_card(card_obj, init_db)
  assert result == True

def test_card_obj_sent_to_update_card_gets_properly_updated(init_db):
  """
  update_card() should take in an object of type knards.Card and update it in
  the DB.
  """
  initial_card_obj = knards.Card()
  initial_card_id = api.create_card(card_obj, init_db)

  stored_card_obj = api.get_card_by_id(initial_card_id, init_db)
  stored_card_obj._replace(question='new contents', score=12)
  api.update_card(stored_card_obj, init_db)

  updated_card_obj = api.get_card_by_id(initial_card_id, init_db)
  assert updated_card_obj.id == initial_card_id
  assert updated_card_obj.question == 'new contents'
  assert updated_card_obj.answer == initial_card_obj.answer
  assert updated_card_obj.markers == initial_card_obj.markers
  assert updated_card_obj.date_created == initial_card_obj.date_created
  assert updated_card_obj.date_updated == datetime.today().strftime('%Y-%m-%d')
  assert initial_card_obj.date_updated is None
