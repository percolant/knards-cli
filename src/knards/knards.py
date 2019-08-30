#!python3

import click
from datetime import datetime
from collections import namedtuple
import readchar
import sys

from knards import api, msg, util


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
  datetime.today().strftime('%Y-%m-%d'),
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
@click.option('--qf/--af', default=True, help='What should be prompted for first? Question or answer?')
def new(qf):
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
  card_obj = Card()

  if qf:
    prompt = 'Markers: []\n'
    prompt += 'Series: []\n'
    prompt += 'No. in series: 1\n'
    prompt += msg.DIVIDER_LINE + '\n'
    prompt += card_obj.question + '\n'

    valid = False
    retry_count = 1
    submit_question = prompt
    while not valid:
      submit_question = util.open_in_editor(submit_question)

      if len(submit_question.split('\n')) < 5:
        submit_question += '\n' * (5 - len(submit_question.split('\n')))

      for index, line in enumerate(submit_question.split('\n')):
        if index == 0 and 'Markers: [' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_MARKERS)
          break
        if index == 1 and 'Series: [' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_SERIES)
          break
        if index == 2 and 'No. in series: ' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_POS_IN_SERIES)
          break
        if index == 3 and line != msg.DIVIDER_LINE:
          print(msg.CLI_ERROR_DONT_CHANGE_DIVIDER_LINE)
          break
        if index > 3 and line == msg.DIVIDER_LINE:
          print(msg.CLI_ERROR_TOO_MANY_DIVIDER_LINES)
          break
      else:
        valid = True

      if not valid:
        print(msg.RETRY)
        retry = readchar.readkey()
        if retry != 'y':
          sys.exit(1)

        # offset one line downwards to make output more readable
        print()

        # allow 3 retries max (anti infinite loop)
        retry_count += 1
        if retry_count > 3:
          sys.exit(1)

    valid = False
    retry_count = 1
    submit_answer = submit_question
    while not valid:
      submit_answer = util.open_in_editor(submit_answer)

      if len(submit_answer.split('\n')) < 5:
        submit_answer += '\n' * (5 - len(submit_answer.split('\n')))

      for index, line in enumerate(submit_answer.split('\n')):
        if index == 0 and 'Markers: [' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_MARKERS)
          break
        if index == 1 and 'Series: [' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_SERIES)
          break
        if index == 2 and 'No. in series: ' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_POS_IN_SERIES)
          break
        if index == 3 and line != msg.DIVIDER_LINE:
          print(msg.CLI_ERROR_DONT_CHANGE_DIVIDER_LINE)
          break
        if index > 3 and line == msg.DIVIDER_LINE:
          print(msg.CLI_ERROR_TOO_MANY_DIVIDER_LINES)
          break
      else:
        valid = True

      if not valid:
        print(msg.RETRY)
        retry = readchar.readkey()
        if retry != 'y':
          sys.exit(1)

        # offset one line downwards to make output more readable
        print()

        # allow 3 retries max (anti infinite loop)
        retry_count += 1
        if retry_count > 3:
          sys.exit(1)

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
    prompt = 'Markers: []\n'
    prompt += 'Series: []\n'
    prompt += 'No. in series: 1\n'
    prompt += msg.DIVIDER_LINE + '\n'
    prompt += card_obj.answer + '\n'

    valid = False
    retry_count = 1
    submit_answer = prompt
    while not valid:
      submit_answer = util.open_in_editor(submit_answer)

      if len(submit_answer.split('\n')) < 5:
        submit_answer += '\n' * (5 - len(submit_answer.split('\n')))

      for index, line in enumerate(submit_answer.split('\n')):
        if index == 0 and 'Markers: [' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_MARKERS)
          break
        if index == 1 and 'Series: [' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_SERIES)
          break
        if index == 2 and 'No. in series: ' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_POS_IN_SERIES)
          break
        if index == 3 and line != msg.DIVIDER_LINE:
          print(msg.CLI_ERROR_DONT_CHANGE_DIVIDER_LINE)
          break
        if index > 3 and line == msg.DIVIDER_LINE:
          print(msg.CLI_ERROR_TOO_MANY_DIVIDER_LINES)
          break
      else:
        valid = True

      if not valid:
        print(msg.RETRY)
        retry = readchar.readkey()
        if retry != 'y':
          sys.exit(1)

        # offset one line downwards to make output more readable
        print()

        # allow 3 retries max (anti infinite loop)
        retry_count += 1
        if retry_count > 3:
          sys.exit(1)

    valid = False
    retry_count = 1
    submit_question = submit_answer
    while not valid:
      submit_question = util.open_in_editor(submit_question)

      if len(submit_question.split('\n')) < 5:
        submit_question += '\n' * (5 - len(submit_question.split('\n')))

      for index, line in enumerate(submit_question.split('\n')):
        if index == 0 and 'Markers: [' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_MARKERS)
          break
        if index == 1 and 'Series: [' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_SERIES)
          break
        if index == 2 and 'No. in series: ' not in line:
          print(msg.CLI_ERROR_DONT_CHANGE_POS_IN_SERIES)
          break
        if index == 3 and line != msg.DIVIDER_LINE:
          print(msg.CLI_ERROR_DONT_CHANGE_DIVIDER_LINE)
          break
        if index > 3 and line == msg.DIVIDER_LINE:
          print(msg.CLI_ERROR_TOO_MANY_DIVIDER_LINES)
          break
      else:
        valid = True

      if not valid:
        print(msg.RETRY)
        retry = readchar.readkey()
        if retry != 'y':
          sys.exit(1)

        # offset one line downwards to make output more readable
        print()

        # allow 3 retries max (anti infinite loop)
        retry_count += 1
        if retry_count > 3:
          sys.exit(1)

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
@click.option('--q/--no-q', default=True, help='Should the output include the question text?')
@click.option('--a/--no-a', default=True, help='Should the output include the answer text?')
@click.option('--inc', help='A marker or a list of markers. Only cards that contain ALL of those markers will be output')
@click.option('--exc', help='A marker or a list of markers. Only cards that do not contain NEITHER of those markers will be output')
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
