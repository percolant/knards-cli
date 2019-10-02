import os
import sqlite3
import subprocess
import tempfile

from knards import knards, config, msg, exceptions


def db_connect(db_path):
  """
  Check if the DB file exists and, if yes, connect to it and return the
  connection handler.
  """
  if not os.path.exists(db_path):
    raise exceptions.DBFileNotFound(
      'DB file ({}) does not exist.'.format(db_path)
    )

  connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
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
