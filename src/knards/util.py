import os
import readchar
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

def check_buffer(subcommand, input_buffer):
  """
  Check if the input buffer is formatted properly.
  Return the buffer if everything is OK.

  TODO: revert invalid buffer to previous state.
  """
  valid = False

  if subcommand == 'new':
    pass
  elif subcommand == 'edit':
    if len(input_buffer.split('\n')) < 5:
      input_buffer += '\n' * (5 - len(input_buffer.split('\n')))

    for index, line in enumerate(input_buffer.split('\n')):
      if index == 0 and 'Markers: [' not in line:
        raise exceptions.BadBufferFormat('First line in the buffer must be of \
the following format: Markers: [markers for the card]')
      if index == 1 and 'Series: [' not in line:
        raise exceptions.BadBufferFormat('Second line in the buffer must be \
of the following format: Series: [name of the series]')
      if index == 2 and 'No. in series: ' not in line:
        raise exceptions.BadBufferFormat('Third line in the buffer must be of \
the following format: No. in series: #')
      if index == 3 and line != msg.DIVIDER_LINE:
        raise exceptions.BadBufferFormat('Fourth line in the buffer must be \
equal to the standard divider line (100x -).')
    else:
      valid = True

    if input_buffer.count(msg.DIVIDER_LINE) > 2:
      raise exceptions.BadBufferFormat('Buffer cannot have more than 2x \
standard divider lines (100x -).')
      valid = False

  return (input_buffer, valid)

def retry_buffer(retry_count):
  """
  This is the method for the buffer retry functionality.
  """
  print(msg.RETRY)
  retry = readchar.readkey()
  if retry != 'y':
    return False

  # allow 3 retries max (anti infinite loop)
  retry_count += 1
  if retry_count > 3:
    return False

  return True
