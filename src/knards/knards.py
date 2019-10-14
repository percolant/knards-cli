#!python3

from blist import blist
import click
from datetime import datetime
from collections import abc, namedtuple
import random
import re
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
  '--inc', 'include_markers', type=str,
  help='A list of markers all of which each card that is to be revised must \
have. Examples: --inc=python; --inc="english, vocabulary"'
)
@click.option(
  '--exc', 'exclude_markers', type=str,
  help='A list of markers none of which each card that is to be revised must \
have. Examples: --exc=python; --exc="english, vocabulary"'
)
def list(q, a, include_markers, exclude_markers):
  """
  Output a set of cards in the set up editor.
  """
  if include_markers is not None:
    include_markers = include_markers.split(',')
  else:
    include_markers = []
  if exclude_markers is not None:
    exclude_markers = exclude_markers.split(',')
  else:
    exclude_markers = []

  # fetch cards from the DB according to the constraints defined by input args
  card_set = api.get_card_set(
    show_question=q,
    show_answer=a,
    include_markers=include_markers,
    exclude_markers=exclude_markers,
  )

  # generate list buffer
  buf = ''
  for card in card_set:
    if card.date_updated is not None:
      date_updated = \
        card.date_updated.strftime('%d %b %Y')
    else:
      date_updated = 'Never'
    buf += msg.CARD_LIST_TEMPLATE.format(
      card.id,
      card.markers,
      card.pos_in_series,
      card.series,
      card.date_created.strftime('%d %b %Y'),
      date_updated,
      card.score,
    )
    if q:
      buf += '\n{}\n'.format(card.question)
      if a:
        buf += '{}\n'.format(msg.DIVIDER_LINE)
    if a:
      buf += '\n{}\n'.format(card.answer)

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
  # Exit codes:
  # 0: success
  # 1: unknown error
  # 2: bad input arguments
  # 3: sqlite3 module exception
  # 4: api method got wrong input
  # 5: DB file not found
  # 6: object not found

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
  # 3: sqlite3 module exception
  # 4: api method got wrong input
  # 5: DB file not found
  # 6: object not found

  if not card_id and not markers:
    with click.Context(delete) as ctx:
      click.echo(delete.get_help(ctx))
    sys.exit(2)

  if markers:
    markers = [
      a for a in \
      re.split(r'(\s|\,)', markers.strip('')) \
      if a != ' ' and a != ','
    ]

  try:
    result = api.delete_card(card_id, markers)
  except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
    click.secho(e.args[0], fg='red', bold=True)
    sys.exit(3)
  except TypeError as e:
    click.secho(e.args[0], fg='red', bold=True)
    sys.exit(4)
  except exceptions.DBFileNotFound as e:
    click.secho(e.args[0], fg='red', bold=True)
    sys.exit(5)
  except exceptions.CardNotFound as e:
    click.secho(e.args[0], fg='red', bold=True)
    sys.exit(6)

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

@main.command()
@click.option(
  '--inc', 'include_markers', type=str, default=[],
  help='A list of markers all of which each card that is to be revised must \
have. Examples: --inc=python; --inc="english, vocabulary"'
)
@click.option(
  '--exc', 'exclude_markers', type=str, default=[],
  help='A list of markers none of which each card that is to be revised must \
have. Examples: --exc=python; --exc="english, vocabulary"'
)
def revise(include_markers, exclude_markers):
  """Revise a set of cards"""

  # Exit codes:
  # 0: success
  # 1: unknown error
  # 2: bad input arguments
  # 3: sqlite3 module exception
  # 4: api method got wrong input
  # 5: DB file not found
  # 6: no cards adhere to constraints

  if include_markers:
    include_markers = [
      a for a in \
      re.split(r'(\s|\,)', include_markers.strip('')) \
      if a != ' ' and a != ','
    ]
  if exclude_markers:
    exclude_markers = [
      a for a in \
      re.split(r'(\s|\,)', exclude_markers.strip('')) \
      if a != ' ' and a != ','
    ]

  try:
    card_set = blist(api.get_card_set(
      include_markers=include_markers,
      exclude_markers=exclude_markers
    ))
    full_card_set = blist(api.get_card_set())
  except TypeError as e:
    click.secho(e.args[0], fg='red', bold=True)
    sys.exit(4)
  except exceptions.DBFileNotFound as e:
    click.secho(e.args[0], fg='red', bold=True)
    sys.exit(5)
  except exceptions.EmptyDB as e:
    click.secho(e.args[0], fg='red', bold=True)
    sys.exit(6)

  # sort the card set
  never_updated = []
  updated = []
  for card in card_set:
    if not card.date_updated:
      never_updated.append(card)
      continue
    updated.append(card)
  updated.sort(key=lambda obj: obj.date_updated)
  never_updated.sort(key=lambda obj: obj.date_created)
  card_set = updated + never_updated

  # proceed to revising cards
  while card_set:
    card_obj = card_set.pop(0)

    # if the card is part of series, pick out all cards of that series
    if card_obj.series:
      try:
        subset = api.get_series_set(card_obj.series)
        subset_length = len(subset)
      except (
        TypeError,
        sqlite3.OperationalError,
        exceptions.DBFileNotFound,
        exceptions.EmptyDB
      ):
        subset = None
        subset_length = None

      assert subset is not None
      assert subset_length is not None

      # all cards from the series must be ready for revision
      series_ready = True
      for series_obj_num in subset:
        if subset[series_obj_num].date_updated is not None:
          if subset[series_obj_num].score > (
            datetime.now().date() - subset[series_obj_num].date_updated.date()
          ).days:
            series_ready = False
            break

      # if not, continue to the next card
      if not series_ready:
        continue

      while subset:
        series_obj = subset.pop(min(subset.keys()))

        try:
          util.ask(series_obj, subset_length)
        except ValueError as e:
          # from api.update_card
          pass
        except sqlite3.OperationalError as e:
          # from api.update_card
          pass

    # else, just ask the question
    else:
      # check if the card is ready to be revised
      if card_obj.date_updated is not None:
        if card_obj.score > (
          datetime.now().date() - card_obj.date_updated.date()
        ).days:
          continue

      try:
        util.ask(card_obj)
      except ValueError as e:
        # from api.update_card
        pass
      except sqlite3.OperationalError as e:
        # from api.update_card
        pass

@main.command()
def status():
  """
  TODO
  """

  total_card_set = api.get_card_set()
  revised_today_set = api.get_card_set(today=True)
  more_revisable = api.get_card_set(revisable_only=True)

  click.secho('There\'re {} cards in the DB file in total.\n\
You\'ve revised {} cards today.\n\
There\'re {} more cards ready for revision today.'.format(
    len(total_card_set),
    len(revised_today_set),
    len(more_revisable)
  ), fg='yellow', bold=True)
