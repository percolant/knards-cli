from datetime import datetime

from knards import knards, api


def test_markers_arg_must_be_a_list_of_strings(init_db):
  """
  get_last_card() takes in an optional argument, markers, that must be a list
  of strings.
  """
  pass

def test_if_no_args_passed_in_method_returns_the_last_stored_card(init_db):
  """
  If no arguments are passed to the get_last_card() method, the method returns
  the card with the largest id from the set of cards with the most recent
  .date_created
  """
  pass

def test_method_returns_none_if_the_DB_is_empty_or_no_cards_found(init_db):
  """
  get_last_card() returns none if the DB is empty or, in case markers were
  passed to the method, no cards were found that contain all the specified
  markers.
  """
  pass

def test_method_returns_a_proper_card_obj_upon_success(init_db):
  """
  get_last_card() returns an object of type knards.Card that is a copy of the
  last stored card object.
  If markers argument is passed to the method, it returns an object of type
  knards.Card that is a copy of the last stored card that has ALL of the
  specified markers.
  """
  pass
