from datetime import datetime, date
import readchar
import sqlite3
import subprocess
import tempfile

from knards import config, msg


def bootstrap_db(db_name):
  """
  TODO
  """
  pass

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
  pass

def update_card(card_obj):
  """
  TODO
  """
  pass

def delete_card(card_id=None, marker=None):
  """
  TODO
  """
  pass
