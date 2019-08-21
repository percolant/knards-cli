#!python3

import click
from datetime import datetime
from collections import namedtuple
import readchar

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
  api.bootstrap_db()

@main.command()
@click.option('--qf/--af', default=True)
def new(qf):
  """
  TODO
  """
  card_obj = Card()

  if qf:
    prompt = 'Markers: []\n'
    prompt += 'Series: []\n'
    prompt += 'No. in series: 1\n'
    prompt += msg.DIVIDER_LINE + '\n'
    prompt += card_obj.question + '\n'

    valid = False
    while not valid:
      submit_question = util.open_in_editor(prompt)

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
          return False

        # offset one line downwards to make output more readable
        print()

    valid = False
    while not valid:
      submit_answer = util.open_in_editor(submit_question)

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
          return False

        # offset one line downwards to make output more readable
        print()

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
    while not valid:
      submit_answer = util.open_in_editor(prompt)

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
          return False

        # offset one line downwards to make output more readable
        print()

    valid = False
    while not valid:
      submit_question = util.open_in_editor(submit_answer)

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
          return False

        # offset one line downwards to make output more readable
        print()

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
@click.option('--q/--no-q', default=True)
@click.option('--a/--no-a', default=True)
@click.option('--inc')
@click.option('--exc')
def list(q, a, inc, exc):
  """
  TODO
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
      date_updated = datetime.strptime(card.date_updated, '%Y-%m-%d').strftime('%d %b %Y')
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


if __name__ == '__main__':
  main()
