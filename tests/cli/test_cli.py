import click
from click.testing import CliRunner
import sys

from knards import knards


def test_main():
  runner = CliRunner()
  result = runner.invoke(knards.main)
  assert result.exit_code == 0
  assert 'Usage' in result.output
