from click.testing import CliRunner
import os
import pytest

from knards import knards, api, config


def test_returns_exit_code_1_upon_failure(mocker):
  """
  Upon any failure in the API, the subcommand must return exit code 1.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    mocker.patch('knards.api.bootstrap_db', return_value=False)

    result = runner.invoke(knards.main, ['bootstrap-db'])
    assert result.exit_code == 1

def test_returns_exit_code_1_if_DB_already_exists():
  """
  The subcommand returns exit code 1 if the DB file already exists.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    # we can't just create the file here, because API fails if the file is an
    # actual DB file and contains the respective table, thus we invoke the
    # subcommand twice
    result = runner.invoke(knards.main, ['bootstrap-db'])
    result = runner.invoke(knards.main, ['bootstrap-db'])
    assert result.exit_code == 1

def test_success_is_when_file_exists_and_exit_code_0_is_returned():
  """
  The subcommand must only return exit code 0 upon the successful invocation.
  Also, check if the actual DB file is present.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    result = runner.invoke(knards.main, ['bootstrap-db'])

    assert result.exit_code == 0
    # file with the DB exists within the temp dir that was created by test
    assert os.path.exists(os.getcwd() + '/' + config.DB)
