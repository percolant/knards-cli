from knards import knards, api


def test_fail_if_db_path_is_not_string():
  """
  bootstrap_db() must fail and return False if passed a non-string argument.
  """
  assert api.bootstrap_db(111) is False

def test_fail_in_has_no_permission_to_write():
  """
  If bootstrap_db() within the script has no permission to write to a file, it
  fails and returns False.
  """
  assert api.bootstrap_db('/test.db') is False
