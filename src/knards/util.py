import click
from datetime import datetime
import os
import re
import readchar
import sqlite3
import subprocess
import sys
import tempfile

from knards import knards, config, msg, exceptions, api


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

def open_in_editor(buf, editor='nvim'):
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

  if subcommand == 'edit':
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

def ask(card_obj, series_length=None):
  """Puts up a text buffer for card revision

  Args:
    card_obj (knards.Card): An object of type knards.Card
    series_length (int): If the card is a part of a series, we will also need
  to know the length of the series

  Raises:
    TODO

  Returns:
    TODO
  """

  if card_obj.date_updated:
    date_updated = card_obj.date_updated.strftime('%d %b %Y')
  else:
    date_updated = 'Never'

  if series_length:
    buffer_title = 'Card #{} | {} | {}/{} in "{}" | {} | {} | {}\n'.format(
      card_obj.id,
      card_obj.markers,
      card_obj.pos_in_series,
      series_length,
      card_obj.series,
      card_obj.date_created.strftime('%d %b %Y'),
      date_updated,
      card_obj.score
    )
  else:
    buffer_title = 'Card #{} | {} | {} | {} | {}\n'.format(
      card_obj.id,
      card_obj.markers,
      card_obj.date_created.strftime('%d %b %Y'),
      date_updated,
      card_obj.score
    )

  buffer_prompt = buffer_title + '{}\n{}\n{}\n{}'.format(
    msg.DIVIDER_LINE,
    card_obj.question,
    msg.DIVIDER_LINE,
    'Replace the question with your answer, then save the buffer and close the\
 editor to submit'
  )

  answer = open_in_editor(buffer_prompt)
  if answer.count(msg.DIVIDER_LINE) != 2 \
    and answer.count(msg.DIVIDER_LINE) != 0:
    print('While revising, either leave both divider lines in the buffer and \
your answer between the two lines, or delete both of them and leave only the \
answer text.')
  else:
    if answer.count(msg.DIVIDER_LINE) == 0:
      answer = answer.strip('\n')
    else:
      answer = answer.split(msg.DIVIDER_LINE)[1].strip('\n')

  buffer_check = buffer_title + '{}\n{}\n{}\n{}\n{}\n{}'.format(
    msg.DIVIDER_LINE,
    answer,
    msg.DIVIDER_LINE,
    card_obj.answer,
    msg.DIVIDER_LINE,
    'Delete all contents of this buffer and leave one of the following \
options:\n\
I know this well (card\'s score becomes equal {})\n\
I\'ve made some minor mistakes (card\'s score becomes equal {})\n\
I had problems with remembering this/I\'ve made critical mistakes \
(card\'s status becomes equal 1)\n\
I do not know this at all (card\'s status becomes equal 0)'.format(
      get_fibonacci_sequence(card_obj.score)[-1],
      get_fibonacci_sequence(card_obj.score)[-3]
    )
  )

  valid = False
  retry_count = 1
  while not valid:
    check = open_in_editor(buffer_check)
    check = check.strip('\n')
    if len(check.split('\n')) > 1:
      click.clear()
      click.echo('You must\'ve had deleted all the contents of the previous \
buffer and leave only one of the offered options (listed underneath the second\
 divider line)')
    elif len(re.findall(r'\d+', check)) > 1:
      click.clear()
      click.echo('You must not alter option\'s text')
    else:
      card_obj = card_obj._replace(date_updated=datetime.now())
      card_obj = card_obj._replace(
        score=re.findall(r'\d+', check)[0]
      )
      api.update_card(card_obj)
      break

    if retry_count > 3:
      break
    else:
      retry_count += 1
    if not click.confirm('Try and resubmit?', default=True):
      break

  click.clear()
  if not click.confirm('Next card?', default=True):
    sys.exit(1)

def get_fibonacci_sequence(target_number):
  """Returns a subset of the Fibonacci numeric sequence up to 'target_number'
  + the next element after that

  Args:
    target_number (int): An integer number, don't have to be a part of the
  Fibonacci sequence

  Raises:
    TODO

  Returns:
    A subset of the Fibonacci numeric sequnce up to the 'target_number' + the
  next element after that
  """

  add1 = 0
  add2 = 1
  seq = [add1, add2]
  while target_number > seq[-1]:
    seq.append(add1 + add2)
    add1 = add2
    add2 = seq[-1]

  if add1 == 0 and add2 == 1:
    seq.append(2)
  else:
    seq.append(add1 + add2)
  return seq
