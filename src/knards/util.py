import os
import sqlite3
import subprocess
import tempfile

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

def open_in_editor(buf, editor='vim'):
  """
  Takes in:
  1. buf - text contents to be output to the editor, buffer.
  2. editor - editor to use, default is vim; other editor possible on in theory
  and are neither tested nor recommended to use :)

  Opens contents of buf in editor and returns what's in the editor's buffer
  upon save & exit (:wq in vim)
  """
  with tempfile.NamedTemporaryFile(suffix=".kn") as tf:
    tf.write(buf.encode('utf-8'))
    tf.flush()
    subprocess.call([editor, tf.name])
    tf.seek(0)
    result = tf.read().decode('utf-8').strip()
  return result
