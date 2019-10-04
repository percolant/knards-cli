#!python3

import click
from datetime import datetime
from collections import abc, namedtuple
import readchar
import sys
import sqlite3

from knards import api, msg, util, exceptions

# card object blueprint
Card = namedtuple(
  'Card',
  [
    'id',
    'pos_in_series',
    'question',
    'answer',
    'markers',
    'series',
    'date_created',
    'date_updated',
    'score'
  ]
)

# card object defaults
Card.__new__.__defaults__ = (
  None,
  0,
  'Here, type in the question text for the new card.',
  'Here, type in the answer text for the new card.',
  '',
  None,
  datetime.now(),
  None,
  0
)


@click.group()
def main():
  pass


@main.command()
def bootstrap_db():
  """
  Initialize the DB.
  Launch this if you haven't got the file with DB (see config.py to set its name)
  """
  if not api.bootstrap_db():
    sys.exit(1)


@main.command()
@click.option(
  '--qf/--af',
  default=True,
  help='What should be prompted for first? Question or answer?'
)
@click.option('--copy-last', default=False, is_flag=True)
@click.option('--copy-from-id', type=int)
def new(qf, copy_last, copy_from_id):
  """
  Prompt to create a new card.

  $ kn new
  Opens a "question-first" buffer in editor, processes what's in the buffer
  after "save & exit", sends into the second buffer (for answer), processes
  what's returned by that, checks if the format is OK, splits up metadata and
  card's text, generates an object of type knards.Card and feeds it to the
  create_card()

  $ kn new --af
  Opens a "answer-first" buffer in editor, processes what's in the buffer
  after "save & exit", sends into the second buffer (for question), processes
  what's returned by that, checks if the format is OK, splits up metadata and
  card's text, generates an object of type knards.Card and feeds it to the
  create_card()
  """

  if copy_last:
    card_obj = api.get_last_card()
    prompt = 'Markers: [{}]\n'.format(card_obj.markers)
    prompt += 'Series: [{}]\n'.format(card_obj.series)
    prompt += 'No. in series: {}\n'.format(card_obj.pos_in_series)
  elif copy_from_id:
    card_obj = api.get_card_by_id(copy_from_id)
    prompt = 'Markers: [{}]\n'.format(card_obj.markers)
    prompt += 'Series: [{}]\n'.format(card_obj.series)
    prompt += 'No. in series: {}\n'.format(card_obj.pos_in_series)
  else:
    card_obj = Card()
    prompt = 'Markers: []\n'
    prompt += 'Series: []\n'
    prompt += 'No. in series: 1\n'

  prompt += msg.DIVIDER_LINE + '\n'

  if qf:
    prompt += card_obj.question + '\n'

    valid = False
    retry_count = 1
    submit_question = prompt
    while not valid:
      submit_question = util.open_in_editor(submit_question)

      try:
        submit_question, valid = util.check_buffer('new', submit_question)
      except exceptions.BadBufferFormat as e:
        print(e.args[0])

      if not valid:
        if not util.retry_buffer(retry_count):
          sys.exit(7)

    valid = False
    retry_count = 1
    submit_answer = submit_question
    while not valid:
      submit_answer = util.open_in_editor(submit_answer)

      try:
        submit_answer, valid = util.check_buffer('new', submit_answer)
      except exceptions.BadBufferFormat as e:
        print(e.args[0])

      if not valid:
        if not util.retry_buffer(retry_count):
          sys.exit(7)

    question_text = ''
    for index, line in enumerate(submit_question.split('\n')):
      if index > 3:
        question_text += line + '\n'
    else:
      card_obj = card_obj._replace(question=question_text)

    answer_text = ''
    for index, line in enumerate(submit_answer.split('\n')):
      if index == 0:
        card_obj = card_obj._replace(markers=line.split('[')[1].split(']')[0])
      if index == 1:
        card_obj = card_obj._replace(series=line.split('[')[1].split(']')[0])
      if index == 2:
        card_obj = card_obj._replace(pos_in_series=int(line.split(':')[1][1:]))
      if index > 3:
        answer_text += line + '\n'
    else:
      card_obj = card_obj._replace(answer=answer_text)

    card_id = api.create_card(card_obj)
    if card_id:
      print(msg.NEW_CARD_SUCCESS.format(card_id))
    else:
      print(msg.NEW_CARD_FAILURE)

  else:
    prompt += card_obj.answer + '\n'

    valid = False
    retry_count = 1
    submit_answer = prompt
    while not valid:
      submit_answer = util.open_in_editor(submit_answer)

      try:
        submit_answer, valid = util.check_buffer('new', submit_answer)
      except exceptions.BadBufferFormat as e:
        print(e.args[0])

      if not valid:
        if not util.retry_buffer(retry_count):
          sys.exit(7)

    valid = False
    retry_count = 1
    submit_question = submit_answer
    while not valid:
      submit_question = util.open_in_editor(submit_question)

      try:
        submit_question, valid = util.check_buffer('new', submit_question)
      except exceptions.BadBufferFormat as e:
        print(e.args[0])

      if not valid:
        if not util.retry_buffer(retry_count):
          sys.exit(7)

    question_text = ''
    for index, line in enumerate(submit_question.split('\n')):
      if index == 0:
        card_obj = card_obj._replace(markers=line.split('[')[1].split(']')[0])
      if index == 1:
        card_obj = card_obj._replace(series=line.split('[')[1].split(']')[0])
      if index == 2:
        card_obj = card_obj._replace(pos_in_series=int(line.split(':')[1][1:]))
      if index > 3:
        question_text += line + '\n'
    else:
      card_obj = card_obj._replace(question=question_text)

    answer_text = ''
    for index, line in enumerate(submit_answer.split('\n')):
      if index > 3:
        answer_text += line + '\n'
    else:
      card_obj = card_obj._replace(answer=answer_text)

    card_id = api.create_card(card_obj)
    if card_id:
      print(msg.NEW_CARD_SUCCESS.format(card_id))
    else:
      print(msg.NEW_CARD_FAILURE)


@main.command()
@click.option(
  '--q/--no-q',
  default=True,
  help='Should the output include the question text?'
)
@click.option(
  '--a/--no-a',
  default=True,
  help='Should the output include the answer text?'
)
@click.option(
  '--inc',
  help='A marker or a list of markers. Only cards that contain ALL of those \
markers will be output'
)
@click.option(
  '--exc',
  help='A marker or a list of markers. Only cards that do not contain NEITHER \
of those markers will be output'
)
def list(q, a, inc, exc):
  """
  Output a set of cards in the set up editor.
  """
  if inc is not None:
    inc_markers_list = inc.split(',')
  else:
    inc_markers_list = []
  if exc is not None:
    exc_markers_list = exc.split(',')
  else:
    exc_markers_list = []

  # fetch cards from the DB according to the constraints defined by input args
  card_set = api.get_card_set(
    show_question=q,
    show_answer=a,
    include_markers=inc_markers_list,
    exclude_markers=exc_markers_list,
  )

  # generate list buffer
  buf = ''
  for card in card_set:
    if card.date_updated is not None:
      date_updated = \
        datetime.strptime(card.date_updated, '%Y-%m-%d').strftime('%d %b %Y')
    else:
      date_updated = 'Never'
    buf += msg.CARD_LIST_TEMPLATE.format(
      card.id,
      card.markers,
      card.pos_in_series,
      card.series,
      datetime.strptime(card.date_created, '%Y-%m-%d').strftime('%d %b %Y'),
      date_updated,
      card.score,
      msg.DIVIDER_LINE,
      card.question,
      msg.DIVIDER_LINE,
      card.answer,
    )

  util.open_in_editor(buf)


@main.command()
@click.option(
  '--id',
  'card_id',
  required=True,
  help='A number. The id of the card to edit'
)
def edit(card_id):
  """
  Open a card for edit. Then update it in the DB.

  Input:
  card_id - target card's id. Must be a proper integer.

  Exit codes:
  0 - success
  1 - error
  2 - CLI args misuse
  3 - api method got wrong input
  4 - sqlite operation error
  5 - DB not found
  6 - card not found in the DB
  7 - user failed to fill in the buffer properly
  """

  # try to fetch the card from the DB
  try:
    card_obj = api.get_card_by_id(card_id)
  except ValueError as e:
    print(e.args[0])
    sys.exit(3)
  except sqlite3.OperationalError:
    print('Couldn\'t connect to the DB, check if the file exists and has \
proper permissions assigned.')
    sys.exit(4)
  except exceptions.DBFileNotFound as e:
    print(e.args[0])
    sys.exit(5)
  except exceptions.CardNotFound as e:
    print(e.args[0])
    sys.exit(6)

  prompt = 'Markers: [{}]\n'.format(card_obj.markers)
  prompt += 'Series: [{}]\n'.format(card_obj.series)
  prompt += 'No. in series: {}\n'.format(card_obj.pos_in_series)

  prompt += msg.DIVIDER_LINE + '\n'
  prompt += card_obj.question + '\n'
  prompt += msg.DIVIDER_LINE + '\n'
  prompt += card_obj.answer + '\n'

  valid = False
  retry_count = 1
  submit = prompt
  while not valid:
    submit = util.open_in_editor(submit)

    try:
      submit, valid = util.check_buffer('edit', submit)
    except exceptions.BadBufferFormat as e:
      print(e.args[0])

    if not valid:
      if not util.retry_buffer(retry_count):
        sys.exit(7)

  # remove redundant empty lines on either side
  submit_meta = submit.split(msg.DIVIDER_LINE)[0].strip('\n').split('\n')
  submit_question = submit.split(msg.DIVIDER_LINE)[1].strip('\n').split('\n')
  submit_answer = submit.split(msg.DIVIDER_LINE)[2].strip('\n').split('\n')

  for index, line in enumerate(submit_meta):
    if index == 0:
      card_obj = card_obj._replace(markers=line.split('[')[1].split(']')[0])
    if index == 1:
      card_obj = card_obj._replace(series=line.split('[')[1].split(']')[0])
    if index == 2:
      card_obj = card_obj._replace(pos_in_series=int(line.split(':')[1][1:]))

  question_text = ''
  for index, line in enumerate(submit_question):
    question_text += line + '\n'
  else:
    card_obj = card_obj._replace(question=question_text)

  answer_text = ''
  for index, line in enumerate(submit_answer):
    answer_text += line + '\n'
  else:
    card_obj = card_obj._replace(answer=answer_text)

  try:
    updated_with_id = api.update_card(card_obj)
  except ValueError as e:
    print(e.args[0])
    sys.exit(3)
  except sqlite3.OperationalError:
    click.secho(
      'Error while trying to update the target record in the DB.',
      fg='red', bold=True
    )
    sys.exit(4)

  click.secho(
    'Card #{} was successfully updated.'.format(updated_with_id),
    fg='green', bold=True
  )

@main.command()
@click.option(
  '--id', 'card_id', type=int,
  help='The id of the card that is to be deleted'
)
@click.option(
  '--m', 'markers', type=str,
  help='A list of markers all of which each card that is to be deleted must \
have. Examples: --m=python; --m="english, vocabulary"'
)
def delete(card_id, markers):
  """Delete a card/cards from the DB"""

  # Exit codes:
  # 0: success
  # 1: unknown error
  # 2: bad input arguments

  if not card_id and not markers:
    with click.Context(delete) as ctx:
      click.echo(delete.get_help(ctx))
    sys.exit(2)

  if markers:
    markers = markers.split(',')

  result = api.delete_card(card_id, markers)
  assert isinstance(result, int) or isinstance(result, abc.Sequence)

  if isinstance(result, int):
    click.secho(
      'Card #{} was successfully deleted.'.format(result),
      fg='green', bold=True
    )
  elif isinstance(result, abc.Sequence):
    click.secho(
      '{} cards were deleted.'.format(len(result)),
      fg='green', bold=True
    )
