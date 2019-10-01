from click.testing import CliRunner
import pytest
import os

from knards import knards, api, util, config, msg


def test_without_id_specified(
  mocker,
):
  """
  If no id is specified, script returns exit code 1.
  """
  pass

def test_target_card_does_not_exist(
  mocker,
):
  """
  If the card with the specified id is not found in the DB, script returns
  exit code 1.
  """
  pass

def test_DB_does_not_exist(
  mocker,
):
  """
  If the DB is not found, script returns exit code 1.
  """
  pass

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
    api.create_card(card_obj1, db_path)
    api.create_card(card_obj2, db_path)

    mocker.patch('knards.util.open_in_editor')
    mocker.patch(
      'knards.api.get_card_by_id',
      return_value=api.get_card_by_id(2, db_path=db_path)
    )

    # invoke the subcommand
    result = runner.invoke(knards.main, ['edit', '--id', '2'])
    assert result.exit_code == 0
    assert card_obj2.markers in util.open_in_editor.call_args_list[0][0][0]
    assert card_obj2.series in util.open_in_editor.call_args_list[0][0][0]
    assert card_obj2.pos_in_series in util.open_in_editor.call_args_list[0][0][0]
    assert card_obj2.question in util.open_in_editor.call_args_list[0][0][0]
    assert card_obj2.answer in util.open_in_editor.call_args_list[0][0][0]
    assert util.open_in_editor.call_args_list[0][0][0].count('msg.DIVIDER_LINE') == 2

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