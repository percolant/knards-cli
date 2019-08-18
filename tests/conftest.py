import os
import pytest
from knards import knards, api


@pytest.fixture(autouse=True)
def init_db(tmpdir):
  """
  TODO
  """
  api.bootstrap_db(str(tmpdir) + '/knards.db')
  yield str(tmpdir) + '/knards.db'
  os.remove(str(tmpdir) + '/knards.db')

@pytest.fixture()
def bad_db_path(tmpdir):
  """
  TODO
  """
  return str(tmpdir) + '/nonexistent.db'
