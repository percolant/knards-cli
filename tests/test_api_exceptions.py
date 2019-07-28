import pytest
from knards import knards, api


def test_bootstrap_db_raises_upon_bad_data():
  """
  bootstrap_db() should raise an exception if called upon bad input:
  Must be one arg of type str
  """
  with pytest.raises(TypeError):
    api.bootstrap_db(100)

def test_create_card_raises_upon_bad_data():
  """
  create_card() should raise an exception if called upon bad input:
  Must be one arg of type knards.Card
  """
  with pytest.raises(TypeError):
    api.create_card('wrong type')

def test_update_card_raises_upon_bad_data():
  """
  update_card() should raise an exception if called upon bad input:
  Must be one arg of type knards.Card
  """
  with pytest.raises(TypeError):
    api.update_card('wrong type')
