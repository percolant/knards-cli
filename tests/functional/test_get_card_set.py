from datetime import datetime, timedelta

from knards import knards, api


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
