from click.testing import CliRunner
import pytest
import sys
import readchar

from knards import knards, api, util


def test_default_mode_is_question_first(
  mocker,
  question_prompt_proper_fill,
  answer_prompt_proper_fill
):
  """
  If the 'new' subcommand is invoked without arguments, like so:
  $ kn new
  the subcommand must work in the "question-first" mode.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=iter([
        question_prompt_proper_fill,
        answer_prompt_proper_fill
      ])
    )

    # invoke the subcommand without arguments
    runner.invoke(knards.main, ['new'])
    # fetch the saved card
    card_obj = api.get_card_by_id(1)
    # check if it has the standard question text in the question field
    assert 'Proper question text.' in card_obj.question
    # and the standard answer text in the answer field
    assert 'Proper answer text.' in card_obj.answer

def test_qf_argument_invokes_question_first_mode(
  mocker,
  question_prompt_proper_fill,
  answer_prompt_proper_fill
):
  """
  If the 'new' subcommand is invoked with the '--qf' option, like so:
  $ kn new --qf
  the subcommand must work in the "question-first" mode.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=iter([
        question_prompt_proper_fill,
        answer_prompt_proper_fill
      ])
    )

    # invoke the subcommand with the respective option
    runner.invoke(knards.main, ['new', '--qf'])
    # fetch the saved card
    card_obj = api.get_card_by_id(1)
    # check if it has the standard question text in the question field
    assert 'Proper question text.' in card_obj.question
    # and the standard answer text in the answer field
    assert 'Proper answer text.' in card_obj.answer

def test_af_argument_invokes_answer_first_mode(
  mocker,
  question_prompt_proper_fill,
  answer_prompt_proper_fill
):
  """
  If the 'new' subcommand is invoked with the '--af' option, like so:
  $ kn new --af
  the subcommand must work in the "answer-first" mode.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=iter([
        answer_prompt_proper_fill,
        question_prompt_proper_fill
      ])
    )

    # invoke the subcommand with the respective option
    runner.invoke(knards.main, ['new', '--af'])
    # fetch the saved card
    card_obj = api.get_card_by_id(1)
    # check if it has the standard question text in the question field
    assert 'Proper question text.' in card_obj.question
    # and the standard answer text in the answer field
    assert 'Proper answer text.' in card_obj.answer

def test_contents_of_the_first_prompted_buffer(
  mocker,
  question_prompt_input,
  answer_prompt_input
):
  """
  The standard "empty" buffer templates are opened in buffers prompted first.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    mocker.patch(
      'knards.util.open_in_editor',
      return_value=None
    )

    result = runner.invoke(knards.main, ['new', '--qf'])
    result.exit_code == 1
    # check that the standard question input template is opened in the question
    # buffer in "question-first" mode
    assert question_prompt_input in util.open_in_editor.call_args_list[0][0][0]

    result = runner.invoke(knards.main, ['new', '--af'])
    result.exit_code == 1
    # check that the standard answer input template is opened in the answer
    # buffer in "answer-first" mode
    assert answer_prompt_input in util.open_in_editor.call_args_list[1][0][0]

def test_contents_of_the_first_prompted_buffer_is_opened_in_the_second_buffer(
  mocker,
  question_prompt_proper_fill
):
  """
  The exact contents of the first saved buffer (in any mode) is then opened in
  the second prompted buffer.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=iter([
        question_prompt_proper_fill,
        None
      ])
    )

    result = runner.invoke(knards.main, ['new'])
    result.exit_code == 1
    # check if the second time the util.open_in_editor is invoked it's invoked
    # with the exact contents returned by the first invocation as argument.
    assert util.open_in_editor.call_args_list[1][0][0] == \
      question_prompt_proper_fill

def test_metadata_is_saved_from_the_second_buffer(
  mocker,
  question_prompt_proper_fill,
  answer_prompt_proper_fill
):
  """
  The card's metadata (markers, series, and position in series) is saved from
  the second prompted buffer. The metadata from the first buffer is ignored.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=iter([
        question_prompt_proper_fill,
        answer_prompt_proper_fill
      ])
    )

    # invoke the subcommand
    runner.invoke(knards.main, ['new'])
    # fetch the saved card
    card_obj = api.get_card_by_id(1)
    # check if it has got markers from the second buffer
    assert 'answer' in card_obj.markers
    assert 'question' not in card_obj.markers
    # check if it has got series from the second buffer
    assert 'answer' in card_obj.series
    assert 'question' not in card_obj.series
    # check if it has got position in series from the second buffer
    assert card_obj.pos_in_series == 3

def test_only_return_exit_code_0_upon_successful_card_save(
  mocker,
  question_prompt_proper_fill,
  answer_prompt_proper_fill
):
  """
  'new' subcommand only returns exit code 0 if there're no errors and the card
  was successfully stored in the DB.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=iter([
        question_prompt_proper_fill,
        answer_prompt_proper_fill
      ])
    )

    # invoke the subcommand
    result = runner.invoke(knards.main, ['new'])
    assert result.exit_code == 0

def test_return_exit_code_1_upon_failed_card_save(
  mocker,
  prompt_bad_fill_empty,
  prompt_bad_fill_no_markers,
  prompt_bad_fill_no_series,
  prompt_bad_fill_no_pos_in_series,
  prompt_bad_fill_no_divider
):
  """
  Saved buffer must adhere to the defined standard of filling - have markers
  data, series data, position in series data, and divider line.
  If not, the card is not stored in the DB and an exit code 1 is returned by
  the script.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=iter([
        prompt_bad_fill_empty,
        prompt_bad_fill_no_markers,
        prompt_bad_fill_no_series,
        prompt_bad_fill_no_pos_in_series,
        prompt_bad_fill_no_divider,
        prompt_bad_fill_empty,
        prompt_bad_fill_no_markers,
        prompt_bad_fill_no_series,
        prompt_bad_fill_no_pos_in_series,
        prompt_bad_fill_no_divider
      ])
    )

    # invoke the subcommand for each buffer
    for i in range(5):
      result = runner.invoke(knards.main, ['new'])
      # each invocation must return exit code 1 since buffers are filled in
      # improperly each time
      assert result.exit_code == 1

    # and for "answer-first" mode
    for i in range(5):
      result = runner.invoke(knards.main, ['new', '--af'])
      assert result.exit_code == 1

def test_user_prompted_for_retry_upon_bad_buffer_format(
  mocker,
  prompt_bad_fill_empty,
  prompt_bad_fill_no_markers,
  prompt_bad_fill_no_series,
  prompt_bad_fill_no_pos_in_series,
  prompt_bad_fill_no_divider
):
  """
  Saved buffer must adhere to the defined standard of filling - have markers
  data, series data, position in series data, and divider line.
  If not, the card is not stored in the DB and "retry" is mentioned in CLI
  output.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=iter([
        prompt_bad_fill_empty,
        prompt_bad_fill_no_markers,
        prompt_bad_fill_no_series,
        prompt_bad_fill_no_pos_in_series,
        prompt_bad_fill_no_divider,
        prompt_bad_fill_empty,
        prompt_bad_fill_no_markers,
        prompt_bad_fill_no_series,
        prompt_bad_fill_no_pos_in_series,
        prompt_bad_fill_no_divider
      ])
    )
    mocker.patch('readchar.readkey', return_value='n')

    # invoke the subcommand for each buffer
    for i in range(5):
      result = runner.invoke(knards.main, ['new'])
      assert 'retry' in result.output.lower()

    # and for "answer-first" mode
    for i in range(5):
      result = runner.invoke(knards.main, ['new', '--af'])
      assert 'retry' in result.output.lower()

def test_retry_sends_the_improperly_filled_buffer_into_editor(
  mocker,
  question_prompt_input,
  prompt_bad_fill_no_markers
):
  """
  Upon the 'y' reply to retry prompt, script sends the improperly filled buffer
  contents to util.open_in_editor, rather than any other (generic or initial)
  buffer contents.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    mocker.patch(
      'knards.util.open_in_editor',
      return_value=prompt_bad_fill_no_markers
    )
    mocker.patch('readchar.readkey', side_effect=iter(['y', 'n']))

    runner.invoke(knards.main, ['new'])
    assert question_prompt_input in util.open_in_editor.call_args_list[0][0][0]
    assert prompt_bad_fill_no_markers in \
      util.open_in_editor.call_args_list[1][0][0]

def test_max_amount_of_retries_is_3(
  mocker,
  question_prompt_input,
  prompt_bad_fill_no_markers
):
  """
  After 3 unsuccessful retries, script fails and returns exit code 1.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    mocker.patch(
      'knards.util.open_in_editor',
      return_value=prompt_bad_fill_no_markers
    )
    mocker.patch('readchar.readkey', return_value='y')

    result = runner.invoke(knards.main, ['new'])
    assert util.open_in_editor.call_count == 3
    assert readchar.readkey.call_count == 3
    assert result.exit_code == 1

def test_copy_last_argument_invokes_first_prompt_with_copy_of_last_cards_text(
  mocker,
  init_db
):
  """
  $ kn new --qf --copy-last
  must prompt for a new card, "question-first" mode; the prompt must be
  prepopulated with data copied from the last stored card.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # create the DB
    runner.invoke(knards.main, ['bootstrap-db'])

    # create some card objs
    card_obj_first = knards.Card(
      markers='pytest',
      series='',
      pos_in_series=1,
      question='some_text',
      answer='some_text_2'
    )
    card_obj_last = knards.Card(
      markers='python test',
      series='test_series',
      pos_in_series=3,
      question='test_quest',
      answer='test_answer'
    )
    api.create_card(card_obj_first, init_db)
    api.create_card(card_obj_last, init_db)

    # trigger method fail upon first invocation of util.open_in_editor()
    mocker.patch(
      'knards.util.open_in_editor',
      side_effect=ValueError
    )
    mocker.patch(
      'knards.api.get_last_card',
      return_value=api.get_last_card(init_db)
    )

    # invoke the subcommand with respective options
    runner.invoke(knards.main, ['new', '--qf', '--copy-last'])
    assert api.get_last_card.call_count == 1
    assert util.open_in_editor.call_count == 1
    assert 'Markers: [{}]'.format(card_obj_last.markers) in \
        util.open_in_editor.call_args_list[0][0][0]
    assert 'Series: [{}]'.format(card_obj_last.series) in \
        util.open_in_editor.call_args_list[0][0][0]
    assert 'No. in series: {}'.format(card_obj_last.pos_in_series) in \
        util.open_in_editor.call_args_list[0][0][0]
    assert 'test_quest' in util.open_in_editor.call_args_list[0][0][0]

@pytest.mark.skip(reason="TODO in future")
def test_cant_type_in_nonint_to_pos_in_series_field():
  """
  TODO
  """
  pass

@pytest.mark.skip(reason="TODO in future")
def test_cant_get_last_card_from_empty_DB():
  """
  TODO
  """
  pass

@pytest.mark.skip(reason="TODO in future")
def test_fields_cant_be_empty_in_a_saved_card():
  """
  Check all fields in a successfully saved card, nothing may be empty.
  Try to save a card with empty text -> must fail.
  """
  pass
