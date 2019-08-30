import sqlite3

from knards import knards, api, msg


def test_bootstrap_db_bad_db_path(mocker):
  """
  If db_path input arg is not a string -> print out an error and return False
  """
  # here, we can't fetch out stdout, so we patch standard print() as a workaround
  mocker.patch('builtins.print')
  result = api.bootstrap_db(111)
  assert result == False
  assert print.call_count == 1
  assert print.call_args[0][0] == msg.DB_PATH_MUST_BE_STR

def test_bootstrap_db_connection_failure(init_db, mocker):
  """
  Upon connection failure -> print out an error and return False
  """
  mocker.patch('builtins.print')
  # here, we simulate sqlite3 connection error
  mocker.patch('sqlite3.connect', side_effect=sqlite3.OperationalError())
  result = api.bootstrap_db(init_db)
  assert result == False
  assert print.call_count == 1
  assert print.call_args[0][0] == \
    msg.CANNOT_CONNECT_TO_DB_PERMISSION_DENIED.format(init_db)

def test_bootstrap_db_query_execution_failure(init_db, mocker):
  """
  Upone SQL query execution error -> print out an error and return False
  """
  mocker.patch('builtins.print')
  # here, we simulate sqlite3 SQL query execution error
  mocked_connect = mocker.patch('sqlite3.connect')
  mocked_connect.cursor.execute.side_effect = sqlite3.OperationalError()
  result = api.bootstrap_db(init_db)
  assert result == False
  assert print.call_count == 1
  assert print.call_args == \
    msg.DB_ALREADY_EXISTS.format(init_db)
