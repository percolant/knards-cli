import os
import pytest
from knards import api


@pytest.fixture()
def init_db(tmpdir):
  """
  Add and use this fixture everywhere you work with the DB. This creates a
  'test.db' DB in the current dir, runs the test with it, and removes the file
  afterwards.
  """
  api.bootstrap_db(str(tmpdir) + '/test.db')
  yield str(tmpdir) + '/test.db'
  os.remove(str(tmpdir) + '/test.db')
