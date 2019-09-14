from datetime import datetime, timedelta

from knards import knards, api


def test_empty_DB_returns_empty_list(init_db):
  """
  get_card_set() upon an empty DB must not raise no exceptions, but return []
  instead.
  """
  assert api.get_card_set(db_path=init_db) == []

def test_returns_list_of_proper_type_objects(init_db):
  """
  get_card_set() must always return either a list of objects of type
  knards.Card or []
  """
  assert api.get_card_set(db_path=init_db) == []

  card_obj = knards.Card()
  api.create_card(card_obj, init_db)

  assert isinstance(api.get_card_set(db_path=init_db), list)
  assert isinstance(api.get_card_set(db_path=init_db)[0], knards.Card)

def test_dates_are_cast_to_convenient_format(init_db):
  """
  sqlite3 keeps dates in UNIX timestamp format, upon each get_card_set() we,
  among other things, cast all dates to 'YYYY-mm-dd' format.
  """
  card_obj = knards.Card(date_created='2019-08-31', date_updated='2019-08-31')
  api.create_card(card_obj, init_db)

  return_value = api.get_card_set(db_path=init_db)
  assert return_value[0].date_created == card_obj.date_created
  assert return_value[0].date_updated == card_obj.date_updated

def test_revisable_only_today_show_question_and_show_answer_must_be_boolean(
  init_db
):
  """
  We don't expect revisable_only/today/show question/show answer to be anything
  other than a boolean.
  """
  card_obj = knards.Card()
  api.create_card(card_obj, init_db)

  # a bunch of different combinations of input args (at least one of them is
  # not of an expected type)
  assert api.get_card_set(revisable_only=1, db_path=init_db) == []
  assert api.get_card_set(revisable_only=True, today=1, db_path=init_db) == []
  assert api.get_card_set(show_question=1, db_path=init_db) == []
  assert api.get_card_set(show_question=1, show_answer=1, db_path=init_db) == []
  assert api.get_card_set(
    revisable_only='not boolean',
    show_question=True,
    today=True
  ) == []
  assert api.get_card_set(
    revisable_only='not boolean',
    show_question=True,
    today=card_obj
  ) == []

def test_if_revisable_only_is_true_return_only_cards_ready_for_revision(init_db):
  """
  If revisable_only=True is passed to get_card_set(), return cards that either
  don't have .date_updated set (None) or have their .score less than or equal
  to the difference between today and its .date_updated in days.
  """
  card_obj1 = knards.Card()
  card_obj2 = knards.Card(
    date_updated=(datetime.today() - timedelta(1)).strftime('%Y-%m-%d'),
    score=1
  )
  card_obj3 = knards.Card(
    date_updated=(datetime.today() - timedelta(1)).strftime('%Y-%m-%d'),
    score=2
  )

  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)

  assert len(api.get_card_set(revisable_only=False, db_path=init_db)) == 3
  assert len(api.get_card_set(revisable_only=True, db_path=init_db)) == 2

def test_input_markers_must_be_lists(init_db):
  """
  We don't expect include_markers/exclude_markers to be anything other than
  lists.
  """
  card_obj = knards.Card()
  api.create_card(card_obj, init_db)

  assert api.get_card_set(include_markers='test', db_path=init_db) == []
  assert api.get_card_set(exclude_markers=111, db_path=init_db) == []
  assert api.get_card_set(
    include_markers=True,
    exclude_markers=111,
    db_path=init_db
  ) == []

def test_if_markers_passed_return_cards_with_respect_to_constraints(init_db):
  """
  If get_card_set() is passed include_markers=[...], return only cards that
  have ALL of the specified markers.
  If get_card_set() is passed exclude_markers=[...], return only cards that
  have NONE of the specified markers.
  """
  card_obj1 = knards.Card(markers='python specific')
  card_obj2 = knards.Card(markers='javascript specific')
  card_obj3 = knards.Card(markers='python nonspecific')
  card_obj4 = knards.Card(markers='javascript test')
  card_obj5 = knards.Card(markers='javascript test special')
  card_obj6 = knards.Card(markers='javascript python')
  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)
  api.create_card(card_obj4, init_db)
  api.create_card(card_obj5, init_db)
  api.create_card(card_obj6, init_db)

  assert len(api.get_card_set(
    include_markers=['test'],
    db_path=init_db
  )) == 2
  assert len(api.get_card_set(
    include_markers=['specific'],
    db_path=init_db
  )) == 2
  assert len(api.get_card_set(
    include_markers=['spec'],
    db_path=init_db
  )) == 0
  assert len(api.get_card_set(
    include_markers=['javascript'],
    db_path=init_db
  )) == 4
  assert len(api.get_card_set(
    include_markers=['special', 'javascript'],
    db_path=init_db
  )) == 1
  assert len(api.get_card_set(
    exclude_markers=['javascript'],
    db_path=init_db
  )) == 2
  assert len(api.get_card_set(
    exclude_markers=['python', 'test'],
    db_path=init_db
  )) == 1
  assert len(api.get_card_set(
    exclude_markers=['specific'],
    db_path=init_db
  )) == 4
  assert len(api.get_card_set(
    exclude_markers=['specific', 'test'],
    db_path=init_db
  )) == 2

def test_if_today_is_true_return_only_cards_that_were_reviewed_today(init_db):
  """
  If today=True is passed to get_card_set(), return cards that have
  .date_updated equal to today's date.
  """
  card_obj1 = knards.Card()
  card_obj2 = knards.Card(
    date_updated=datetime.today().strftime('%Y-%m-%d'),
    score=1
  )
  card_obj3 = knards.Card(
    date_created=(datetime.today() - timedelta(10)).strftime('%Y-%m-%d'),
    score=2
  )

  api.create_card(card_obj1, init_db)
  api.create_card(card_obj2, init_db)
  api.create_card(card_obj3, init_db)

  assert len(api.get_card_set(today=True, db_path=init_db)) == 1
  assert len(api.get_card_set(today=False, db_path=init_db)) == 3
