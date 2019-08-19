import os
from click.testing import CliRunner

from knards import knards, api, config, msg, util


def test_main():
  """
  $ kn --help
  Outputs basic help info on knards. Must contain info about all possible
  commands.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    result = runner.invoke(knards.main, ['--help'])

    assert result.exit_code == 0
    assert 'Usage' in result.output
    assert 'bootstrap-db' in result.output

def test_bootstrap_db():
  """
  $ kn bootstrap-db
  Creates a DB with the name specified in the config.py module. If the DB
  already exists, does nothing and ends silently.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    result = runner.invoke(knards.main, ['bootstrap-db'])

    # subcommand returned success
    assert result.exit_code == 0
    # subcommand output success message
    assert result.output == msg.BOOTSTRAP_DB_SUCCESS.format(config.DB) + '\n'
    # file with the DB exists within the temp dir that was created by test
    assert os.path.exists(os.getcwd() + '/' + config.DB)

def test_new(mocker):
  """
  $ kn new
  Opens a "question-first" buffer in editor, 
  """
  card_obj = knards.Card()
  question_first_prompt = 'Markers: []\n'
  question_first_prompt += 'Series: []\n'
  question_first_prompt += 'No. in series: 1\n'
  question_first_prompt += msg.DIVIDER_LINE + '\n'
  question_first_prompt += card_obj.question + '\n'
  question_first_output = 'Markers: [test markers]\n'
  question_first_output += 'Series: [test series]\n'
  question_first_output += 'No. in series: 2\n'
  question_first_output += msg.DIVIDER_LINE + '\n'
  question_first_output += 'Test question' + '\n'
  answer_first_prompt = 'Markers: []\n'
  answer_first_prompt += 'Series: []\n'
  answer_first_prompt += 'No. in series: 1\n'
  answer_first_prompt += msg.DIVIDER_LINE + '\n'
  answer_first_prompt += card_obj.answer + '\n'
  answer_first_output = 'Markers: [test markers]\n'
  answer_first_output += 'Series: [test series]\n'
  answer_first_output += 'No. in series: 2\n'
  answer_first_output += msg.DIVIDER_LINE + '\n'
  answer_first_output += 'Test answer' + '\n'

  runner = CliRunner()
  with runner.isolated_filesystem():
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch(
      'knards.util.open_in_editor',
      return_value=question_first_output
    )

    result = runner.invoke(knards.main, ['new'])
    assert util.open_in_editor.call_count == 2
    assert util.open_in_editor.call_args_list[0][0][0] == question_first_prompt
    assert util.open_in_editor.call_args_list[1][0][0] == question_first_output

    assert result.exit_code == 0

    mocker.patch(
      'knards.util.open_in_editor',
      return_value=answer_first_output
    )

    result = runner.invoke(knards.main, ['new', '--af'])
    assert util.open_in_editor.call_count == 2
    assert util.open_in_editor.call_args_list[0][0][0] == answer_first_prompt
    assert util.open_in_editor.call_args_list[1][0][0] == answer_first_output

    assert result.exit_code == 0

    first_obj = api.get_card_by_id(1)
    assert 'Test question' in first_obj.answer

    second_obj = api.get_card_by_id(2)
    assert 'Test answer' in second_obj.question
