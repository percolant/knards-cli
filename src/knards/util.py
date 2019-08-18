import os
import sqlite3

from knards import knards, config, msg


def db_connect(db_path):
  """
  Takes in a DB file path.
  Returns sqlite connection handler or None upon failure.
  """
  # connection might fail here if the script has no permission to write to
  # db_path
  try:
    connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
  except sqlite3.OperationalError:
    print(msg.CANNOT_CONNECT_TO_DB_PERMISSION_DENIED.format(db_path))
    return None

  cursor = connection.cursor()

  # if DB file doesn't exist, the default behavior is to create it, which is
  # not we want -> False is returned upon such event
  try:
    cursor.execute("""
      SELECT * FROM cards
    """)
  except sqlite3.OperationalError:
    print(msg.CANNOT_CONNECT_TO_DB_NO_DB.format(db_path))
    connection.close()
    os.remove(db_path)
    return None

  cursor.close()
  return connection
