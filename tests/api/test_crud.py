from datetime import datetime, timedelta

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

def test_create_card_return_valid_id(init_db):
  """
  api.create_card() takes in a knards.Card object, stores it in the DB and
  returns the id it was created with.
  """
  new_card = knards.Card()
  new_card_id = api.create_card(new_card, init_db)
  assert isinstance(new_card_id, int)

def test_create_card_index_generation(init_db):
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
  assert api.delete_card(card_id=2, db_path=init_db)
  card_id = api.create_card(card_obj1, init_db)
  assert card_id == 2

def test_get_card_set_processes_constraints(init_db):
  """
  Create some cards and try to fetch them out of the DB specifying different
  constraint sets to see if the method works properly.
  The method must return a list of objects of type knards.Card
  """
  card_obj1 = knards.Card(
    question='_question_',
    answer='_answer_',
    markers='python specific',
  )
  card_obj2 = knards.Card(
    question='_question_',
    answer='_answer_',
    markers='javascript specific',
    score=20,
  )
  card_obj3 = knards.Card(
    question='_question_',
    answer='_answer_',
    markers='nonspecific',
    score=2,
    date_updated=(datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
  )
  card_obj4 = knards.Card(
    question='_question_',
    answer='_answer_',
    score=1,
    date_updated=datetime.today().strftime('%Y-%m-%d')
  )
  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)
  api.create_card(card_obj4, init_db)

  result = api.get_card_set(db_path=init_db)
  # check if method returns a list of knards.Card objects
  for obj in result:
    assert isinstance(obj, knards.Card)
  # no constraints specified -> returns all cards in the DB
  assert len(result) == 4
  assert result[0].question == '_question_'
  assert result[1].answer == '_answer_'
  assert result[2].markers == 'nonspecific'
  assert result[1].id == 2
  assert result[0].date_created == datetime.today().strftime('%Y-%m-%d')
  assert result[2].date_updated != datetime.today().strftime('%Y-%m-%d')

  result = api.get_card_set(
    revisable_only=True,
    db_path=init_db
  )
  # only return cards that are ready to be revised
  # this means cards that either have date_updated == None
  # or score <= difference of today's date and date_updated in days
  assert len(result) == 2
  assert result[0].score == 0
  assert result[1].score == 20

  result = api.get_card_set(
    today=True,
    db_path=init_db
  )
  # only return cards that were already revised today
  # this means cards that have date_updated == today
  assert len(result) == 1

  result = api.get_card_set(
    show_question=False,
    include_markers=['specific'],
    db_path=init_db
  )
  # returns all cards that have 'specific' within their markers
  assert len(result) == 2
  # output must not contain question text, only answer
  assert result[0].question == ''
  assert result[1].question == ''
  assert result[0].answer == '_answer_'
  assert result[1].answer == '_answer_'
  # results must not include cards that have 'nonspecific' within their markers
  # and not 'specific'; markers are checked word-wise
  assert 'nonspecific' not in result[0].markers
  assert 'nonspecific' not in result[1].markers

  result = api.get_card_set(
    show_question=False,
    show_answer=False,
    include_markers=['specific'],
    exclude_markers=['python'],
    db_path=init_db
  )
  # only return cards that have 'specific' within their markers and not
  # 'python'
  assert len(result) == 1
  # results must not include question or answer texts, only metadata
  assert result[0].question == ''
  assert result[0].answer == ''
  assert result[0].markers == 'javascript specific'
