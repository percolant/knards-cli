#!python3

import click
from datetime import datetime
import os
from collections import namedtuple
import re
import readchar
import random
import sys
from termcolor import colored, cprint

from knards import config


# card object blueprint
Card = namedtuple(
  'Card',
  [
    'id',
    'pos_in_series',
    'question',
    'answer',
    'markers',
    'series',
    'date_created',
    'date_updated',
    'score'
  ]
)

# card object defaults
Card.__new__.__defaults__ = (
  None,
  0,
  'Here, type in the question text for the new card.',
  'Here, type in the answer text for the new card.',
  '',
  None,
  datetime.today().strftime('%Y-%m-%d'),
  datetime.today().strftime('%Y-%m-%d'),
  0
)


@click.group()
def main():
  pass

if __name__ == '__main__':
  main()
