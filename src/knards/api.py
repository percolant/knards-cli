from datetime import datetime, date
import readchar
import sqlite3
import subprocess
import tempfile

from knards import knards, config, msg


def bootstrap_db(db_name):
  """
  TODO
  """
  if type(db_name) is not str:
    raise TypeError('Input arg must be of type str')

def get_card_set(
    revisable_only=False,
    show_question=True,
    show_answer=True,
    include_markers=[],
    exclude_markers=[],
    today=False
  ):
  """
  TODO
  """
  pass

def create_card(card_obj):
  """
  TODO
  """
  if type(card_obj) is not knards.Card:
    raise TypeError('Input arg must be of type Card')

def update_card(card_obj):
  """
  TODO
  """
  if type(card_obj) is not knards.Card:
    raise TypeError('Input arg must be of type Card')

def delete_card(card_id=None, marker=None):
  """
  TODO
  """
  pass
