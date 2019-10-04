from click.testing import CliRunner
import os
import pytest

from knards import knards, api, config


def test_without_args_specified():
  """
  If neither 'card id', nor 'markers' input arg is specified, script returns
  exit code 2
  """

  runner = CliRunner()
  with runner.isolated_filesystem():
    result = runner.invoke(knards.main, ['delete'])
    assert result.exit_code == 2

def test_DB_does_not_exist(mocker):
  """
  If the DB is not found, script returns exit code 5.
  """

  runner = CliRunner()
  with runner.isolated_filesystem():
    db_path = os.getcwd() + '/' + config.DB
    mocker.patch('knards.config.get_DB_name', return_value=db_path)

    result = runner.invoke(knards.main, ['delete', '--id', 1])
    assert result.exit_code == 5

def test_card_id_must_be_proper_integer():
  """
  'card id' input arg must be a proper integer, defining the id of the card we
  want to delete. Otherwise, script must return exit code 2
  """

  runner = CliRunner()
  with runner.isolated_filesystem():
    result = runner.invoke(knards.main, ['delete', '--id', 'a'])
    assert result.exit_code == 2

def test_markers_option_is_properly_translated_to_list(mocker):
  """
  1. --m=python must be translated to ['python']
  2. --m="python,REST API" must be translated to ['python', 'REST API']
  3. --m english must be translated to ['english']
  4. --m "phrases,english" must be translated to ['phrases', 'english']

  For some reason, we can't really test for double quotes here, although it
  works perfectly actually.
  """

  runner = CliRunner()
  with runner.isolated_filesystem():
    mocker.patch('knards.api.delete_card', side_effect=Exception)

    result = runner.invoke(knards.main, ['delete', '--m', 'python'])
    assert result.exit_code == 1
    assert api.delete_card.call_args_list[0][0][1] == ['python']
    result = runner.invoke(knards.main, ['delete', '--m', 'python,REST API'])
    assert result.exit_code == 1
    assert api.delete_card.call_args_list[1][0][1] == ['python', 'REST', 'API']
    result = runner.invoke(knards.main, ['delete', '--m', 'english'])
    assert result.exit_code == 1
    assert api.delete_card.call_args_list[2][0][1] == ['english']
    result = runner.invoke(knards.main, ['delete', '--m', 'phrases,english'])
    assert result.exit_code == 1
    assert api.delete_card.call_args_list[3][0][1] == ['phrases', 'english']

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

    # invoke the subcommand
    result = runner.invoke(knards.main, ['delete', '--id', 1])
    assert result.exit_code == 6

def test_a_single_card_is_properly_deleted_if_card_id_is_specified(mocker):
  """
  If 'card id' arg is specified, delete the card that has that id from the DB.
  """

  card_obj1 = knards.Card()
  card_obj2 = knards.Card()

  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])
    db_path = os.getcwd() + '/' + config.DB
    mocker.patch('knards.config.get_DB_name', return_value=db_path)

    # create cards
    api.create_card(card_obj1)
    api.create_card(card_obj2)

    # check that cards were successfully stored
    assert len(api.get_card_set()) == 2

    # invoke the subcommand
    result = runner.invoke(knards.main, ['delete', '--id', 1])
    assert result.exit_code == 0

    # one card should be deleted, the one that's left must have an id = 2
    assert len(api.get_card_set()) == 1
    assert api.get_card_set()[0].id == 2

def test_all_cards_containing_all_markers_are_deleted_if_markers_is_specified(
  mocker
):
  """
  If 'markers' arg is specified, delete ALL the cards that have ALL the markers
  that are specified.
  """

  card_obj1 = knards.Card(markers='python specific test')
  card_obj2 = knards.Card(markers='python')
  card_obj3 = knards.Card(markers='python specific test')
  card_obj4 = knards.Card(markers='python specifico test')

  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])
    db_path = os.getcwd() + '/' + config.DB
    mocker.patch('knards.config.get_DB_name', return_value=db_path)

    # create cards
    api.create_card(card_obj1)
    api.create_card(card_obj2)
    api.create_card(card_obj3)
    api.create_card(card_obj4)

    # check that cards were successfully stored
    assert len(api.get_card_set()) == 4

    # invoke the subcommand
    result = runner.invoke(
      knards.main,
      ['delete', '--m', 'python,specific test']
    )
    assert result.exit_code == 0

    # two cards should be deleted, two that's left have ids 2 and 4
    assert len(api.get_card_set()) == 2
    assert api.get_card_set()[0].id == 2
    assert api.get_card_set()[1].id == 4

    # in development we don't allow to delete all cards at once using markers
    result = runner.invoke(knards.main, ['delete', '--m', 'python'])
    assert result.exit_code == 1
    assert len(api.get_card_set()) == 2

def test_if_both_id_and_markers_are_specified_ignores_markers(mocker):
  """
  If both 'card id' and 'markers' args are specified, 'markers' are ignored.
  """

  card_obj1 = knards.Card(markers='python specific test')
  card_obj2 = knards.Card(markers='python')
  card_obj3 = knards.Card(markers='python specific test')

  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])
    db_path = os.getcwd() + '/' + config.DB
    mocker.patch('knards.config.get_DB_name', return_value=db_path)

    # create cards
    api.create_card(card_obj1)
    api.create_card(card_obj2)
    api.create_card(card_obj3)

    # check that cards were successfully stored
    assert len(api.get_card_set()) == 3

    # invoke the subcommand
    result = runner.invoke(
      knards.main, ['delete', '--id', 1, '--m', 'python']
    )
    assert result.exit_code == 0
    assert len(api.get_card_set()) == 2
