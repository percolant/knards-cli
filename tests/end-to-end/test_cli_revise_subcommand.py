from click.testing import CliRunner
import os
import pytest

from knards import knards, api, config


def test_markers_option_is_properly_translated_to_list(mocker):
  """
  1. --inc=python must be translated to ['python']
  2. --inc="python,REST API" must be translated to ['python', 'REST', 'API']
  3. --exc english must be translated to ['english']
  4. --exc "phrases,english" must be translated to ['phrases', 'english']

  For some reason, we can't really test for double quotes here, although it
  works perfectly actually.
  """

  runner = CliRunner()
  with runner.isolated_filesystem():
    mocker.patch('knards.api.get_card_set', side_effect=Exception)

    runner.invoke(knards.main, ['revise', '--inc', 'python'])
    assert api.get_card_set.call_args_list[0][1]['include_markers'] == \
      ['python']

    runner.invoke(knards.main, ['revise', '--inc', 'python,REST API'])
    assert api.get_card_set.call_args_list[1][1]['include_markers'] == \
      ['python', 'REST', 'API']

    runner.invoke(knards.main, ['revise', '--exc', 'english'])
    assert api.get_card_set.call_args_list[2][1]['exclude_markers'] == \
      ['english']

    runner.invoke(knards.main, ['revise', '--exc', 'phrases,english'])
    assert api.get_card_set.call_args_list[3][1]['exclude_markers'] == \
      ['phrases', 'english']
