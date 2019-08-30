import pytest

from knards import knards, api


@pytest.mark.onetimeish
def test_performance_on_11000_cards(init_db):
  """
  In this test we simulate a creation of 11000 cards (and storing them in the
  DB) and the following fetching for them in the DB, with respect to different
  constraints specified.
  """
  for i in range(10000):
    api.create_card(knards.Card(markers='first second third'), init_db)

  for i in range(1000):
    api.create_card(knards.Card(markers='first second fourth'), init_db)

  set1 = api.get_card_set(include_markers=['second'], db_path=init_db)
  set2 = api.get_card_set(include_markers=['second', 'third'], db_path=init_db)
  set3 = api.get_card_set(
    include_markers=['second'],
    exclude_markers=['third'],
    db_path=init_db
  )

  assert len(set1) == 11000
  assert len(set2) == 10000
  assert len(set3) == 1000

def test_performance_on_1100_cards(init_db):
  """
  In this test we simulate a creation of 1100 cards (and storing them in the
  DB) and the following fetching for them in the DB, with respect to different
  constraints specified.
  """
  for i in range(1000):
    api.create_card(knards.Card(markers='first second third'), init_db)

  for i in range(100):
    api.create_card(knards.Card(markers='first second fourth'), init_db)

  set1 = api.get_card_set(include_markers=['second'], db_path=init_db)
  set2 = api.get_card_set(include_markers=['second', 'third'], db_path=init_db)
  set3 = api.get_card_set(
    include_markers=['second'],
    exclude_markers=['third'],
    db_path=init_db
  )

  assert len(set1) == 1100
  assert len(set2) == 1000
  assert len(set3) == 100
