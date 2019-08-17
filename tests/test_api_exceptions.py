import pytest
from knards import knards, api


def test_bootstrap_db_input_args():
  """
  bootstrap_db() should raise an exception if called upon bad input:
  Must be one arg of type str
  """
  with pytest.raises(TypeError) as excinfo:
    api.bootstrap_db(100)
  error_msg = excinfo.value.args[0]
  assert error_msg == 'Input arg must be of type str'

def test_get_card_by_id_input_args():
  """
  get_card_by_id() should raise an exception if called upon bad input:
  Must be one arg of type int
  """
  with pytest.raises(TypeError) as excinfo:
    api.get_card_by_id(card_id='text')
  error_msg = excinfo.value.args[0]
  assert error_msg == 'Target card\'s id must be an integer number'

def test_create_card_input_args():
  """
  create_card() should raise an exception if called upon bad input:
  Must be one arg of type knards.Card
  """
  with pytest.raises(TypeError) as excinfo:
    api.create_card('wrong type')
  error_msg = excinfo.value.args[0]
  assert error_msg == 'Input arg must be of type Card'

def test_update_card_input_args():
  """
  update_card() should raise an exception if called upon bad input:
  Must be one arg of type knards.Card
  """
  with pytest.raises(TypeError) as excinfo:
    api.update_card('wrong type')
  error_msg = excinfo.value.args[0]
  assert error_msg == 'Input arg must be of type Card'

def test_delete_card_input_args():
  """
  delete_card() should raise an exception if called upon bad input:
  Takes up to two optional args: the first must be an integer and the second
  must be a string.
  """
  with pytest.raises(TypeError) as excinfo:
    api.delete_card(card_id='text')
  error_msg = excinfo.value.args[0]
  assert error_msg == 'Target card\'s id must be an integer number'

  with pytest.raises(TypeError) as excinfo:
    api.delete_card(marker=100)
  error_msg = excinfo.value.args[0]
  assert error_msg == 'Markers list must be a string'

  # if the first arg is defined -> ignore the second one
  assert api.delete_card(100, 100) == True

  # if no args passed -> return True (do nothing)
  assert api.delete_card() == True
