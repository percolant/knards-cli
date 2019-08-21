from datetime import datetime

from knards import knards


def test_card_object_defaults():
  """
  Using no parameters should invoke defaults.
  """
  card_1 = knards.Card()
  card_2 = knards.Card(
    None,
    0,
    'Here, type in the question text for the new card.',
    'Here, type in the answer text for the new card.',
    '',
    None,
    datetime.today().strftime('%Y-%m-%d'),
    None,
    0
  )
  assert card_1 == card_2

def test_card_object_member_access():
  """
  Check .field functionality of namedtuple.
  """
  card = knards.Card(question='test', score=1)
  assert card.id is None
  assert card.pos_in_series == 0
  assert card.question == 'test'
  assert card.answer == 'Here, type in the answer text for the new card.'
  assert card.markers == ''
  assert card.series is None
  assert card.date_created == datetime.today().strftime('%Y-%m-%d')
  assert card.date_updated is None
  assert card.score == 1
