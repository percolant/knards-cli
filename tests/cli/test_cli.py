from click.testing import CliRunner

from knards import knards, config, msg


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

  assert result.exit_code == 0
  assert result.output == msg.BOOTSTRAP_DB_SUCCESS.format(config.DB) + '\n'
