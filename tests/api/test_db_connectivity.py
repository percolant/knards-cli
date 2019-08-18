import os

from knards import util


def test_db_connect_with_permission_denied():
  """
  If a filename is passed to db_connect() as the DB file to connect to and the
  script has no permissions to access it -> error is printed out (tested in
  CLI tests) and None is returned.
  """
  connection = util.db_connect('/knards.db')
  assert connection is None

def test_db_connect_with_uninitialized_db():
  """
  If a filename is passed to db_connect() as the DB file to connect to and the
  file doesn't exist (but the path is accessible) - the default behavior of
  sqlite3 is to create the file from scratch (we don't want this) - error is
  printed out (tested in CLI tests) and None is returned.
  Also, method must clean up after itself -> the db_path file mustn't exist
  after the method returns.
  """
  connection = util.db_connect('knards.db')
  assert connection is None

  assert not os.path.exists('knards.db')
