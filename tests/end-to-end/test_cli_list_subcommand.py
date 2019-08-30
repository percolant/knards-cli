from click.testing import CliRunner
import os
import pytest

from knards import knards, api, util, config


def test_markers_option_is_properly_translated_to_list(mocker):
  """
  1. --inc=python must be translated to ['python']
  2. --inc="python,REST API" must be translated to ['python', 'REST API']
  3. --exc english must be translated to ['english']
  4. --exc "phrases,english" must be translated to ['phrases', 'english']

  For some reason, we can't really test for double quotes here, although it
  works perfectly actually.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    mocker.patch('knards.api.get_card_set', return_value=False)

    runner.invoke(knards.main, ['list', '--inc', 'python'])
    assert api.get_card_set.call_args_list[0][1]['include_markers'] == \
      ['python']

    runner.invoke(knards.main, ['list', '--inc', 'python,REST API'])
    assert api.get_card_set.call_args_list[1][1]['include_markers'] == \
      ['python', 'REST API']

    runner.invoke(knards.main, ['list', '--exc', 'english'])
    assert api.get_card_set.call_args_list[2][1]['exclude_markers'] == \
      ['english']

    runner.invoke(knards.main, ['list', '--exc', 'phrases,english'])
    assert api.get_card_set.call_args_list[3][1]['exclude_markers'] == \
      ['phrases', 'english']

def test_if_q_and_a_are_true_question_and_answer_texts_are_present_in_output(
  mocker
):
  """
  If not specified explicitly otherwise, like so:
  $ kn list --no-q --no-a
  the question and/or answer texts must be present in the subcommand's output.
  """
  card_obj = knards.Card()

  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])
    # store the card
    db_path = os.getcwd() + '/' + config.DB
    api.create_card(card_obj, db_path)

    mocker.patch('knards.util.open_in_editor')

    runner.invoke(knards.main, ['list'])
    assert 'question' in util.open_in_editor.call_args_list[0][0][0].lower()
    assert 'answer' in util.open_in_editor.call_args_list[0][0][0].lower()

    runner.invoke(knards.main, ['list', '--q', '--a'])
    assert 'question' in util.open_in_editor.call_args_list[1][0][0].lower()
    assert 'answer' in util.open_in_editor.call_args_list[1][0][0].lower()

def test_if_q_and_a_are_false_question_and_answer_texts_are_not_in_output(
  mocker
):
  """
  If specified explicitly to omit the question/answer text, like so:
  $ kn list --no-q --no-a
  the question and/or answer texts must not be present in the output.
  """
  card_obj = knards.Card()

  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])
    # store the card
    db_path = os.getcwd() + '/' + config.DB
    api.create_card(card_obj, db_path)

    mocker.patch('knards.util.open_in_editor')

    runner.invoke(knards.main, ['list', '--no-q'])
    assert 'question' not in util.open_in_editor.call_args_list[0][0][0].lower()
    assert 'answer' in util.open_in_editor.call_args_list[0][0][0].lower()

    runner.invoke(knards.main, ['list', '--no-q', '--no-a'])
    assert 'question' not in util.open_in_editor.call_args_list[1][0][0].lower()
    assert 'answer' not in util.open_in_editor.call_args_list[1][0][0].lower()

def test_if_card_has_date_updated_none_its_swapped_with_never_in_output(
  mocker
):
  """
  If a card in the DB has its .date_updated equal None, it's displayed as
  "Never" in the subcommand's output.
  .date_updated equals None by default for every new card.
  """
  card_obj1 = knards.Card()
  card_obj2 = knards.Card(date_updated='2019-08-30')
  card_obj3 = knards.Card()

  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])
    # store the card
    db_path = os.getcwd() + '/' + config.DB
    api.create_card(card_obj1, db_path)
    api.create_card(card_obj2, db_path)
    api.create_card(card_obj3, db_path)

    mocker.patch('knards.util.open_in_editor')

    runner.invoke(knards.main, ['list'])
    assert util.open_in_editor.call_args_list[0][0][0].count('Never') == 2

def test_resulting_list_is_opened_in_editor_and_then_exit_code_0(mocker):
  """
  'list' subcommand is expected to fetch a list of cards with respect to the
  specified set of constraints, launch the set up editor, display the card data
  in it, and return exit code 0.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch('knards.util.open_in_editor')

    result = runner.invoke(knards.main, ['list'])
    assert result.exit_code == 0
    assert util.open_in_editor.call_count == 1
