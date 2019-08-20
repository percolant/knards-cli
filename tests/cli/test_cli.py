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
  Opens a "question-first" buffer in editor, processes what's in the buffer
  after "save & exit", sends into the second buffer (for answer), processes
  what's returned by that, checks if the format is OK, splits up metadata and
  card's text, generated an object of type knards.Card

  $ kn new --af
  Opens a "answer-first" buffer in editor, processes what's in the buffer
  after "save & exit", sends into the second buffer (for question), processes
  what's returned by that, checks if the format is OK, splits up metadata and
  card's text, generated an object of type knards.Card
  """
  card_obj = knards.Card()
  # ..._prompt is what's first passed to the open_in_editor method
  # ..._output is what's returned and then passed to the second invocation of
  # open_in_editor
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
  answer_first_output += 'No. in series: 3\n'
  answer_first_output += msg.DIVIDER_LINE + '\n'
  answer_first_output += 'Test answer' + '\n'

  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    # mock the open_in_editor method
    # it must return ..._output
    mocker.patch(
      'knards.util.open_in_editor',
      return_value=question_first_output
    )

    # run the subcommand
    result = runner.invoke(knards.main, ['new'])
    # open_in_editor method must be invoked 2 times
    assert util.open_in_editor.call_count == 2
    # first, ..._prompt is passed to it
    assert util.open_in_editor.call_args_list[0][0][0] == question_first_prompt
    # then, what was returned by the first invocation - ..._output
    assert util.open_in_editor.call_args_list[1][0][0] == question_first_output

    assert result.exit_code == 0

    # now the same but for when '--af' option is specified
    mocker.patch(
      'knards.util.open_in_editor',
      return_value=answer_first_output
    )

    result = runner.invoke(knards.main, ['new', '--af'])
    assert util.open_in_editor.call_count == 2
    assert util.open_in_editor.call_args_list[0][0][0] == answer_first_prompt
    assert util.open_in_editor.call_args_list[1][0][0] == answer_first_output

    assert result.exit_code == 0

    # check if cards were stored in the DB
    first_obj = api.get_card_by_id(1)
    assert 'Test question' in first_obj.answer

    second_obj = api.get_card_by_id(2)
    assert 'Test answer' in second_obj.question

    # finally, check if errors are properly reported in case of failure
    mocker.patch('knards.util.open_in_editor', return_value='')
    result = runner.invoke(knards.main, ['new'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_DONT_CHANGE_MARKERS + '\n' + \
                            msg.RETRY + '\n'

    mocker.patch('knards.util.open_in_editor', return_value='\n'.join([
      'Markers: []',
    ]))
    result = runner.invoke(knards.main, ['new'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_DONT_CHANGE_SERIES + '\n' + \
                            msg.RETRY + '\n'

    mocker.patch('knards.util.open_in_editor', return_value='\n'.join([
      'Markers: []',
      'Series: []',
    ]))
    result = runner.invoke(knards.main, ['new'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_DONT_CHANGE_POS_IN_SERIES + '\n' + \
                            msg.RETRY + '\n'

    mocker.patch('knards.util.open_in_editor', return_value='\n'.join([
      'Markers: []',
      'Series: []',
      'No. in series: 1',
    ]))
    result = runner.invoke(knards.main, ['new'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_DONT_CHANGE_DIVIDER_LINE + '\n' + \
                            msg.RETRY + '\n'

    mocker.patch('knards.util.open_in_editor', return_value='\n'.join([
      'Markers: []',
      'Series: []',
      'No. in series: 1',
      msg.DIVIDER_LINE,
      msg.DIVIDER_LINE,
      msg.DIVIDER_LINE,
    ]))
    result = runner.invoke(knards.main, ['new'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_TOO_MANY_DIVIDER_LINES + '\n' + \
                            msg.RETRY + '\n'

    # the same for '--af' mode
    mocker.patch('knards.util.open_in_editor', return_value='')
    result = runner.invoke(knards.main, ['new', '--af'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_DONT_CHANGE_MARKERS + '\n' + \
                            msg.RETRY + '\n'

    mocker.patch('knards.util.open_in_editor', return_value='\n'.join([
      'Markers: []',
    ]))
    result = runner.invoke(knards.main, ['new', '--af'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_DONT_CHANGE_SERIES + '\n' + \
                            msg.RETRY + '\n'

    mocker.patch('knards.util.open_in_editor', return_value='\n'.join([
      'Markers: []',
      'Series: []',
    ]))
    result = runner.invoke(knards.main, ['new', '--af'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_DONT_CHANGE_POS_IN_SERIES + '\n' + \
                            msg.RETRY + '\n'

    mocker.patch('knards.util.open_in_editor', return_value='\n'.join([
      'Markers: []',
      'Series: []',
      'No. in series: 1',
    ]))
    result = runner.invoke(knards.main, ['new', '--af'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_DONT_CHANGE_DIVIDER_LINE + '\n' + \
                            msg.RETRY + '\n'

    mocker.patch('knards.util.open_in_editor', return_value='\n'.join([
      'Markers: []',
      'Series: []',
      'No. in series: 1',
      msg.DIVIDER_LINE,
      msg.DIVIDER_LINE,
      msg.DIVIDER_LINE,
    ]))
    result = runner.invoke(knards.main, ['new', '--af'])

    assert result.exit_code != 0
    assert result.output == msg.CLI_ERROR_TOO_MANY_DIVIDER_LINES + '\n' + \
                            msg.RETRY + '\n'
