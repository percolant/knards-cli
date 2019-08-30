import pytest

from knards import knards, msg


@pytest.fixture()
def question_prompt_input():
  card_obj = knards.Card()

  return '''Markers: []\nSeries: []\nNo. in series: 1\n{}\n{}\
'''.format(msg.DIVIDER_LINE, card_obj.question)

@pytest.fixture()
def question_prompt_proper_fill():
  return '''Markers: [question marker]\nSeries: [question series]\n\
No. in series: 2\n{}\nProper question text.\n\
'''.format(msg.DIVIDER_LINE)

@pytest.fixture()
def answer_prompt_input():
  card_obj = knards.Card()

  return '''Markers: []\nSeries: []\nNo. in series: 1\n{}\n{}\
'''.format(msg.DIVIDER_LINE, card_obj.answer)

@pytest.fixture()
def answer_prompt_proper_fill():
  return '''Markers: [answer marker]\nSeries: [answer series]\n\
No. in series: 3\n{}\nProper answer text.\n\
'''.format(msg.DIVIDER_LINE)

@pytest.fixture()
def prompt_bad_fill_empty():
  return ''

@pytest.fixture()
def prompt_bad_fill_no_markers():
  card_obj = knards.Card()

  return '''Series: []\nNo. in series: 1\n{}\n{}\n\
'''.format(msg.DIVIDER_LINE, card_obj.question)

@pytest.fixture()
def prompt_bad_fill_no_series():
  card_obj = knards.Card()

  return '''Markers: []\nNo. in series: 1\n{}\n{}\n\
'''.format(msg.DIVIDER_LINE, card_obj.question)

@pytest.fixture()
def prompt_bad_fill_no_pos_in_series():
  card_obj = knards.Card()

  return '''Markers: []\nSeries: []\n{}\n{}\n\
'''.format(msg.DIVIDER_LINE, card_obj.question)

@pytest.fixture()
def prompt_bad_fill_no_divider():
  card_obj = knards.Card()

  return '''Markers: []\nSeries: []\nNo. in series: 1\n{}\n\
'''.format(card_obj.question)
