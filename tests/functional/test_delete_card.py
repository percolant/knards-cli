from datetime import datetime, timedelta

from knards import knards, api


def test_card_id_arg_must_be_a_number(init_db):
  """
  One of the arguments delete_card() takes in is card_id, which must be a
  proper integer number.
  """
  pass

def test_markers_arg_must_be_a_list_of_strings(init_db):
  """
  One of the arguments delete_card() takes in is markers, which must be a list
  of strings.
  """
  pass

def test_if_card_id_is_passed_in_method_deletes_the_card_with_that_id(init_db):
  """
  If card_id argument is passed to the delete_card() method, the card with
  that id is removed from the DB.
  """
  pass

def test_if_card_id_is_passed_in_and_card_doesnt_exist_method_returns_false(
  init_db
):
  """
  If card_id argument is passed to the delete_card() method and the respective
  card doesn't exist in the DB, method returns False and nothing is removed
  from the DB.
  """
  pass

def test_if_markers_passed_in_all_cards_with_those_markers_are_removed(
  init_db
):
  """
  If markers list is passed to the delete_card() method, all cards that contain
  ALL of the specified markers are being removed from the DB.
  """
  pass

def test_if_markers_passed_in_method_returns_true_always(init_db):
  """
  If no cards contain the specified set of markers, no cards are removed from
  the DB and True is returned.
  """
  pass

def test_if_card_id_and_markers_are_passed_in_markers_are_ignored(init_db):
  """
  If both card_id and markers are passed to the delete_card() method, markers
  are ignored and only the card with the card_id id is removed from the DB.
  """
  pass
