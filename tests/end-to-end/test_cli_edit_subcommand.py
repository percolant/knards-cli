import click
from click.testing import CliRunner
import pytest
import os

from knards import knards, api, util, config, msg


def test_without_id_specified():
  """
  If no id is specified, script returns exit code 2 (CLI standard exit code for
  CLI args misuse)
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    result = runner.invoke(knards.main, ['edit'])
    assert result.exit_code == 2

def test_card_id_must_be_proper_integer():
  """
  Card id argument must be a proper integer number. Otherwise, script returns
  exit code 3.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    result = runner.invoke(knards.main, ['edit', '--id', 'a'])
    assert result.exit_code == 3

def test_DB_does_not_exist(mocker):
  """
  If the DB is not found, script returns exit code 5.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    db_path = os.getcwd() + '/' + config.DB
    mocker.patch('knards.config.get_DB_name', return_value=db_path)

    result = runner.invoke(knards.main, ['edit', '--id', 1])
    assert result.exit_code == 5

def test_target_card_does_not_exist(mocker):
  """
  If the card with the specified id is not found in the DB, script returns
  exit code 6.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])
    db_path = os.getcwd() + '/' + config.DB
    mocker.patch('knards.config.get_DB_name', return_value=db_path)

    mocker.patch('knards.util.open_in_editor')

    # invoke the subcommand
    result = runner.invoke(knards.main, ['edit', '--id', 1])
    assert result.exit_code == 6

def test_buffer_contains_metadata_question_and_answer(mocker):
  """
  The buffer that is opened in the editor contains all card's metadata, the
  question text, and the answer text.
  """
  card_obj1 = knards.Card()
  card_obj2 = knards.Card(
    markers='python specific',
    series='Some Series',
    pos_in_series=3,
    question='Some Text For The Question',
    answer='A sample answer'
  )

  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    # store the card
    db_path = os.getcwd() + '/' + config.DB
    mocker.patch('knards.config.get_DB_name', return_value=db_path)

    api.create_card(card_obj1)
    api.create_card(card_obj2)

    mocker.patch('knards.util.open_in_editor', side_effect=Exception)

    # invoke the subcommand
    result = runner.invoke(knards.main, ['edit', '--id', 2])
    assert result.exit_code == 1
    assert card_obj2.markers in util.open_in_editor.call_args_list[0][0][0]
    assert card_obj2.series in util.open_in_editor.call_args_list[0][0][0]
    assert str(card_obj2.pos_in_series) in \
      util.open_in_editor.call_args_list[0][0][0]
    assert card_obj2.question in util.open_in_editor.call_args_list[0][0][0]
    assert card_obj2.answer in util.open_in_editor.call_args_list[0][0][0]
    assert \
      util.open_in_editor.call_args_list[0][0][0].count(msg.DIVIDER_LINE) == 2

def test_card_is_successfully_saved_into_db(
  mocker,
):
  """
  After the opened buffer edited and saved, the card is successfully save into
  DB.
  """
  pass

def test_date_updated_is_updated_to_todays(
  mocker,
):
  """
  After successful edit, the .date_updated of the card is updated to be equal
  to the today's date.
  """
  pass
