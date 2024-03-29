#!python3

import click
from datetime import datetime
from collections import abc, namedtuple
import os
import re
from shutil import copyfile
import sys
import sqlite3

from knards import api, msg, util, exceptions, config

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
    datetime.now(),
    None,
    0
)


@click.group()
def main():
    pass


@main.command()
def bootstrap_db():
    """
    Initialize the DB.
    Launch this if you haven't got the file with DB (see config.py to set its name)
    """
    if not api.bootstrap_db():
        sys.exit(1)


@main.command()
@click.option(
    '--qf/--af',
    default=True,
    help='What should be prompted for first? Question or answer?'
)
@click.option('--copy-last', default=False, is_flag=True)
@click.option('--copy-from-id', type=int)
@click.option(
    '--m', 'markers', type=str,
    help='When creating a new card out of a last added, you may specify a set \
of markers all of which the target card must have. Examples: --m=python; \
--m="english,vocabulary"'
)
def new(qf, copy_last, copy_from_id, markers):
    """
    Prompt to create a new card.

    $ kn new
    Opens a "question-first" buffer in editor, processes what's in the buffer
    after "save & exit", sends into the second buffer (for answer), processes
    what's returned by that, checks if the format is OK, splits up metadata and
    card's text, generates an object of type knards.Card and feeds it to the
    create_card()

    $ kn new --af
    Opens a "answer-first" buffer in editor, processes what's in the buffer
    after "save & exit", sends into the second buffer (for question), processes
    what's returned by that, checks if the format is OK, splits up metadata and
    card's text, generates an object of type knards.Card and feeds it to the
    create_card()
    """

    if markers is not None:
        markers = markers.split(',')
    else:
        markers = []

    if copy_last:
        card_obj = api.get_last_card(markers=markers)
        prompt = 'Markers: [{}]\n'.format(card_obj.markers)
        prompt += 'Series: [{}]\n'.format(card_obj.series)
    elif copy_from_id:
        card_obj = api.get_card_by_id(copy_from_id)
        prompt = 'Markers: [{}]\n'.format(card_obj.markers)
        prompt += 'Series: [{}]\n'.format(card_obj.series)
    else:
        card_obj = Card()
        prompt = 'Markers: []\n'
        prompt += 'Series: []\n'

    card_obj = card_obj._replace(date_created=datetime.now())
    card_obj = card_obj._replace(date_updated=None)
    if card_obj.series:
        card_obj = card_obj._replace(pos_in_series=card_obj.pos_in_series + 1)
    else:
        card_obj = card_obj._replace(pos_in_series=card_obj.pos_in_series)
    card_obj = card_obj._replace(score=0)

    prompt += 'No. in series: {}\n'.format(card_obj.pos_in_series)
    prompt += msg.DIVIDER_LINE + '\n'

    if qf:
        prompt += card_obj.question + '\n'

        valid = False
        retry_count = 1
        submit_question = prompt
        while not valid:
            submit_question = util.open_in_editor(submit_question)

            try:
                submit_question, valid = util.check_buffer('new', submit_question)
            except exceptions.BadBufferFormat as e:
                print(e.args[0])

            if not valid:
                if not util.retry_buffer(retry_count):
                    sys.exit(7)

        valid = False
        retry_count = 1
        submit_answer = submit_question
        while not valid:
            submit_answer = util.open_in_editor(submit_answer)

            try:
                submit_answer, valid = util.check_buffer('new', submit_answer)
            except exceptions.BadBufferFormat as e:
                print(e.args[0])

            if not valid:
                if not util.retry_buffer(retry_count):
                    sys.exit(7)

        question_text = ''
        for index, line in enumerate(submit_question.split('\n')):
            if index > 3:
                question_text += line + '\n'
        else:
            card_obj = card_obj._replace(question=question_text)

        answer_text = ''
        for index, line in enumerate(submit_answer.split('\n')):
            if index == 0:
                card_obj = card_obj._replace(markers=line.split('[')[1].split(']')[0])
            if index == 1:
                card_obj = card_obj._replace(series=line.split('[')[1].split(']')[0])
            if index == 2:
                card_obj = card_obj._replace(pos_in_series=int(line.split(':')[1][1:]))
            if index > 3:
                answer_text += line + '\n'
        else:
            card_obj = card_obj._replace(answer=answer_text)

        card_id = api.create_card(card_obj)
        if card_id:
            click.secho(
                msg.NEW_CARD_SUCCESS.format(card_id),
                fg='green', bold=True
            )
        else:
            click.secho(
                msg.NEW_CARD_FAILURE,
                fg='red', bold=True
            )

    else:
        prompt += card_obj.answer + '\n'

        valid = False
        retry_count = 1
        submit_answer = prompt
        while not valid:
            submit_answer = util.open_in_editor(submit_answer)

            try:
                submit_answer, valid = util.check_buffer('new', submit_answer)
            except exceptions.BadBufferFormat as e:
                print(e.args[0])

            if not valid:
                if not util.retry_buffer(retry_count):
                    sys.exit(7)

        valid = False
        retry_count = 1
        submit_question = submit_answer
        while not valid:
            submit_question = util.open_in_editor(submit_question)

            try:
                submit_question, valid = util.check_buffer('new', submit_question)
            except exceptions.BadBufferFormat as e:
                print(e.args[0])

            if not valid:
                if not util.retry_buffer(retry_count):
                    sys.exit(7)

        question_text = ''
        for index, line in enumerate(submit_question.split('\n')):
            if index == 0:
                card_obj = card_obj._replace(markers=line.split('[')[1].split(']')[0])
            if index == 1:
                card_obj = card_obj._replace(series=line.split('[')[1].split(']')[0])
            if index == 2:
                card_obj = card_obj._replace(pos_in_series=int(line.split(':')[1][1:]))
            if index > 3:
                question_text += line + '\n'
        else:
            card_obj = card_obj._replace(question=question_text)

        answer_text = ''
        for index, line in enumerate(submit_answer.split('\n')):
            if index > 3:
                answer_text += line + '\n'
        else:
            card_obj = card_obj._replace(answer=answer_text)

        card_id = api.create_card(card_obj)
        if card_id:
            click.secho(
                msg.NEW_CARD_SUCCESS.format(card_id),
                fg='green', bold=True
            )
        else:
            click.secho(
                msg.NEW_CARD_FAILURE,
                fg='red', bold=True
            )


@main.command()
@click.option(
    '--q/--no-q',
    default=True,
    help='Should the output include the question text?'
)
@click.option(
    '--a/--no-a',
    default=True,
    help='Should the output include the answer text?'
)
@click.option(
    '--inc', 'include_markers', type=str,
    help='A list of markers all of which each card that is to be revised must \
have. Examples: --inc=python; --inc="english,vocabulary"'
)
@click.option(
    '--exc', 'exclude_markers', type=str,
    help='A list of markers none of which each card that is to be revised must \
have. Examples: --exc=python; --exc="english,vocabulary"'
)
def list(q, a, include_markers, exclude_markers):
    """
    Output a set of cards in the set up editor.
    """
    if include_markers is not None:
        include_markers = include_markers.split(',')
    else:
        include_markers = []
    if exclude_markers is not None:
        exclude_markers = exclude_markers.split(',')
    else:
        exclude_markers = []

    # fetch cards from the DB according to the constraints defined by input args
    card_set = api.get_card_set(
        show_question=q,
        show_answer=a,
        include_markers=include_markers,
        exclude_markers=exclude_markers,
    )

    # generate list buffer
    buf = ''
    for card in card_set:
        if card.date_updated is not None:
            date_updated = \
                card.date_updated.strftime('%d %b %Y')
        else:
            date_updated = 'Never'
        buf += msg.CARD_LIST_TEMPLATE.format(
            card.id,
            card.markers,
            card.pos_in_series,
            card.series,
            card.date_created.strftime('%d %b %Y'),
            date_updated,
            card.score,
        )
        if q:
            buf += '\n{}\n'.format(card.question)
            if a:
                buf += '{}\n'.format(msg.DIVIDER_LINE)
        if a:
            buf += '\n{}\n'.format(card.answer)

    util.open_in_editor(buf)


@main.command()
@click.option(
    '--id',
    'card_id',
    required=True,
    help='A number. The id of the card to edit'
)
def edit(card_id):
    """
    Open a card for edit. Then update it in the DB.

    Input:
    card_id - target card's id. Must be a proper integer.

    Exit codes:
    0 - success
    1 - error
    2 - CLI args misuse
    3 - api method got wrong input
    4 - sqlite operation error
    5 - DB not found
    6 - card not found in the DB
    7 - user failed to fill in the buffer properly
    """
    # Exit codes:
    # 0: success
    # 1: unknown error
    # 2: bad input arguments
    # 3: sqlite3 module exception
    # 4: api method got wrong input
    # 5: DB file not found
    # 6: object not found

    # try to fetch the card from the DB
    try:
        card_obj = api.get_card_by_id(card_id)
    except ValueError as e:
        print(e.args[0])
        sys.exit(3)
    except sqlite3.OperationalError:
        print('Couldn\'t connect to the DB, check if the file exists and has \
proper permissions assigned.')
        sys.exit(4)
    except exceptions.DBFileNotFound as e:
        print(e.args[0])
        sys.exit(5)
    except exceptions.CardNotFound as e:
        print(e.args[0])
        sys.exit(6)

    prompt = 'Markers: [{}]\n'.format(card_obj.markers)
    prompt += 'Series: [{}]\n'.format(card_obj.series)
    prompt += 'No. in series: {}\n'.format(card_obj.pos_in_series)

    prompt += msg.DIVIDER_LINE + '\n'
    prompt += card_obj.question + '\n'
    prompt += msg.DIVIDER_LINE + '\n'
    prompt += card_obj.answer + '\n'

    valid = False
    retry_count = 1
    submit = prompt
    while not valid:
        submit = util.open_in_editor(submit)

        try:
            submit, valid = util.check_buffer('edit', submit)
        except exceptions.BadBufferFormat as e:
            print(e.args[0])

        if not valid:
            if not util.retry_buffer(retry_count):
                sys.exit(7)

    # remove redundant empty lines on either side
    submit_meta = submit.split(msg.DIVIDER_LINE)[0].strip('\n').split('\n')
    submit_question = submit.split(msg.DIVIDER_LINE)[1].strip('\n').split('\n')
    submit_answer = submit.split(msg.DIVIDER_LINE)[2].strip('\n').split('\n')

    for index, line in enumerate(submit_meta):
        if index == 0:
            card_obj = card_obj._replace(markers=line.split('[')[1].split(']')[0])
        if index == 1:
            card_obj = card_obj._replace(series=line.split('[')[1].split(']')[0])
        if index == 2:
            card_obj = card_obj._replace(pos_in_series=int(line.split(':')[1][1:]))

    question_text = ''
    for index, line in enumerate(submit_question):
        question_text += line + '\n'
    else:
        card_obj = card_obj._replace(question=question_text)

    answer_text = ''
    for index, line in enumerate(submit_answer):
        answer_text += line + '\n'
    else:
        card_obj = card_obj._replace(answer=answer_text)

    try:
        updated_with_id = api.update_card(card_obj)
    except ValueError as e:
        print(e.args[0])
        sys.exit(3)
    except sqlite3.OperationalError:
        click.secho(
          'Error while trying to update the target record in the DB.',
          fg='red', bold=True
        )
        sys.exit(4)

    click.secho(
        'Card #{} was successfully updated.'.format(updated_with_id),
        fg='green', bold=True
    )


@main.command()
@click.option(
    '--id', 'card_id', type=int,
    help='The id of the card that is to be deleted'
)
@click.option(
    '--m', 'markers', type=str,
    help='A list of markers all of which each card that is to be deleted must \
have. Examples: --m=python; --m="english, vocabulary"'
)
@click.option(
    '--s', 'series', type=str,
    help='The name of the series that is to be deleted'
)
def delete(card_id, markers, series):
    """Delete a card/cards from the DB"""

    # Exit codes:
    # 0: success
    # 1: unknown error
    # 2: bad input arguments
    # 3: sqlite3 module exception
    # 4: api method got wrong input
    # 5: DB file not found
    # 6: object not found

    if not card_id and not markers and not series:
        with click.Context(delete) as ctx:
            click.echo(delete.get_help(ctx))
        sys.exit(2)

    if markers:
        markers = [
            a for a in \
            re.split(r'(\s|\,)', markers.strip('')) \
            if a != ' ' and a != ','
        ]

    try:
        result = api.delete_card(card_id, markers, series)
    except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
        click.secho(e.args[0], fg='red', bold=True)
        sys.exit(3)
    except TypeError as e:
        click.secho(e.args[0], fg='red', bold=True)
        sys.exit(4)
    except exceptions.DBFileNotFound as e:
        click.secho(e.args[0], fg='red', bold=True)
        sys.exit(5)
    except exceptions.CardNotFound as e:
        click.secho(e.args[0], fg='red', bold=True)
        sys.exit(6)

    assert isinstance(result, int) or isinstance(result, abc.Sequence)

    if isinstance(result, int):
        click.secho(
            'Card #{} was successfully deleted.'.format(result),
            fg='green', bold=True
        )
    elif isinstance(result, abc.Sequence):
        click.secho(
            '{} cards were deleted.'.format(len(result)),
            fg='green', bold=True
        )


@main.command()
@click.option(
    '--inc', 'include_markers', type=str,
    help='A list of markers all of which each card that is to be revised must \
have. Examples: --inc=python; --inc="english, vocabulary"'
)
@click.option(
    '--exc', 'exclude_markers', type=str,
    help='A list of markers none of which each card that is to be revised must \
have. Examples: --exc=python; --exc="english, vocabulary"'
)
def revise(include_markers, exclude_markers):
    """Revise a set of cards"""

    # Exit codes:
    # 0: success
    # 1: unknown error
    # 2: bad input arguments
    # 3: sqlite3 module exception
    # 4: api method got wrong input
    # 5: DB file not found
    # 6: no cards adhere to constraints

    if include_markers:
        include_markers = [
            a for a in \
            re.split(r'(\s|,)', include_markers.strip(''))
            if a != ' ' and a != ','
        ]
    else:
        include_markers = []
    if exclude_markers:
        exclude_markers = [
            a for a in \
            re.split(r'(\s|,)', exclude_markers.strip(''))
            if a != ' ' and a != ','
        ]
    else:
        exclude_markers = []

    try:
        card_set = api.get_card_set(
            include_markers=include_markers,
            exclude_markers=exclude_markers
        )
    except TypeError as e:
        click.secho(e.args[0], fg='red', bold=True)
        sys.exit(4)
    except exceptions.DBFileNotFound as e:
        click.secho(e.args[0], fg='red', bold=True)
        sys.exit(5)
    except exceptions.EmptyDB as e:
        click.secho(e.args[0], fg='red', bold=True)
        sys.exit(6)

    # sort the card set
    never_updated = []
    updated = []
    for card in card_set:
        if not card.date_updated:
            never_updated.append(card)
            continue
        updated.append(card)
    updated.sort(key=lambda obj: (obj.score, obj.date_updated))
    never_updated.sort(key=lambda obj: obj.date_created)

    # we want this: first go all cards that were ever revised, then unrevised
    card_set = never_updated + updated

    # proceed to revising cards
    while card_set:
        card_obj = card_set.pop(0)

        # if the card is part of series, pick out all cards of that series
        if card_obj.series:
            try:
                subset = api.get_series_set(card_obj.series)
                subset_length = len(subset)
            except (
                TypeError,
                sqlite3.OperationalError,
                exceptions.DBFileNotFound,
                exceptions.EmptyDB
            ):
                subset = {1: card_obj}
                subset_length = 1

            filtered_subset = {}
            for series_obj_num in subset:
                if subset[series_obj_num].date_updated is not None:
                    if subset[series_obj_num].score < (
                        datetime.now().date() - subset[series_obj_num].date_updated.date()
                    ).days:
                        filtered_subset[series_obj_num] = subset[series_obj_num]
                else:
                    filtered_subset[series_obj_num] = subset[series_obj_num]

            while filtered_subset:
                series_obj = filtered_subset.pop(min(filtered_subset.keys()))

                try:
                    util.ask(series_obj, subset_length)
                except ValueError as e:
                    # from api.update_card
                    pass
                except sqlite3.OperationalError as e:
                    # from api.update_card
                    pass

        # else, just ask the question
        else:
            # check if the card is ready to be revised
            if card_obj.date_updated is not None:
                if card_obj.score > (
                    datetime.now().date() - card_obj.date_updated.date()
                ).days:
                    continue

            try:
                util.ask(card_obj)
            except ValueError as e:
                # from api.update_card
                pass
            except sqlite3.OperationalError as e:
                # from api.update_card
                pass


@main.command()
@click.option(
    '--inc', 'include_markers', type=str,
    help='A list of markers all of which each card that is to be revised must \
have. Examples: --inc=python; --inc="english, vocabulary"'
)
@click.option(
    '--exc', 'exclude_markers', type=str,
    help='A list of markers none of which each card that is to be revised must \
have. Examples: --exc=python; --exc="english, vocabulary"'
)
def status(include_markers, exclude_markers):
    """
    TODO
    """

    if include_markers:
        include_markers = [
            a for a in \
            re.split(r'(\s|,)', include_markers.strip(''))
            if a != ' ' and a != ','
        ]
    else:
        include_markers = []
    if exclude_markers:
        exclude_markers = [
            a for a in \
            re.split(r'(\s|,)', exclude_markers.strip(''))
            if a != ' ' and a != ','
        ]
    else:
        exclude_markers = []

    total_card_set = api.get_card_set(
        include_markers=include_markers,
        exclude_markers=exclude_markers
    )
    revised_today_set = api.get_card_set(
        today=True,
        include_markers=include_markers,
        exclude_markers=exclude_markers
    )
    more_revisable = api.get_card_set(
        revisable_only=True,
        include_markers=include_markers,
        exclude_markers=exclude_markers
    )

    click.secho('There\'re {} cards in the DB file in total.\n\
You\'ve revised {} cards today.\n\
There\'re {} more cards ready for revision today.'.format(
        len(total_card_set),
        len(revised_today_set),
        len(more_revisable)
    ), fg='yellow', bold=True)


@main.command()
@click.option(
    '--db', 'db_file', type=str,
    help='The path to the DB file that will be merge into the default DB file \
(one that\'s set in config.py)'
)
def merge(db_file):
    """
    TODO
    """

    # check if merge file exists and is a proper DB file
    try:
        with util.db_connect(db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM cards
            """)
            card_set = cursor.fetchall()

        card_set_as_objects = []
        for card in card_set:
            card_set_as_objects.append(Card(*card))

        full_card_set = api.get_card_set()
        dates = []
        for card in full_card_set:
            dates.append(card.date_created)

    except exceptions.DBFileNotFound as e:
        print(e.args[0])
        sys.exit(1)
    except sqlite3.DatabaseError:
        print('{} is not a proper DB file to merge.'.format(db_file))
        sys.exit(1)

    # backup both DB files
    try:
        copyfile(
            config.get_DB_name(),
            config.get_backup_path() + 'main_{}'.format(
                datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
            )
        )
    except IOError as e:
        print("Unable to copy file. %s" % e)
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info())
        sys.exit(1)

    try:
        copyfile(
            db_file,
            config.get_backup_path() + 'merge_{}'.format(
                datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
            )
        )
    except IOError as e:
        print("Unable to copy file. %s" % e)
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info())
        sys.exit(1)

    # merge
    merged = 0
    skipped = 0
    for card in card_set_as_objects:
        if card.date_created in dates:
            skipped += 1
            continue

        merged += 1
        api.create_card(card)

    if skipped == 0:
        click.secho(
            'DB file ({}) was successfully merged into the default DB file.'.format(
                db_file
            ), fg='green', bold=True
        )

        os.remove(db_file)
    else:
        click.secho(
            '{} cards merged; {} cards skipped; You might be trying to merge a DB \
      file that was already merged.\nMerged DB file wasn\'t removed in case \
      something went wrong, please check manually and then remove the file.'.format(
                merged,
                skipped
            ), fg='red', bold=True
        )

@main.command()
def recommend():
    """
    [WIP] Command to show recommendations.
    """
    tags_groups_indexes = [i for i, key in enumerate(config.get_tags_list())]
    tags_groups_names = [key for i, key in enumerate(config.get_tags_list())]
    tags_groups_total_amounts = []
    tags_groups_ready_for_revision = []

    for group_name in tags_groups_names:
        tags_groups_total_amounts.append(len(api.get_card_set(
            include_markers=[group_name]
        )))
        tags_groups_ready_for_revision.append(len(api.get_card_set(
            revisable_only=True,
            include_markers=[group_name]
        )))

    group_indexes_to_revise = []
    group_indexes_to_learn = []

    for index in tags_groups_indexes:
        if ((tags_groups_total_amounts[index]
                / (tags_groups_ready_for_revision[index] + 1)) > 2
                or tags_groups_total_amounts[index] == 0):
            group_indexes_to_learn.append(index)
        else:
            group_indexes_to_revise.append(index)

    if len(group_indexes_to_learn) == 0:
        click.secho(
            'Nothing to learn just yet.\n',
            fg='red', bold=True
        )
    else:
        for index in group_indexes_to_learn:
            sorted_by_priority = {}
            for tag in config.get_tags_list()[tags_groups_names[index]]:
                if tag in config.get_tags_only_revise_list():
                    continue

                total = len(api.get_card_set(include_markers=[tag]))
                if total not in sorted_by_priority:
                    sorted_by_priority[total] = []
                sorted_by_priority[total].append(tag)

            what = tags_groups_names[index]
            tags = sorted_by_priority[
                min([val for i, val in enumerate(sorted_by_priority)])
            ]

            click.secho(
                'Learn {}: {}.\n'.format(what, ', '.join(tags)),
                fg='green', bold=True
            )

    for index in group_indexes_to_revise:
        sorted_by_priority = {}
        for tag in config.get_tags_list()[tags_groups_names[index]]:
            total = api.get_card_set(include_markers=[tag])
            revisable = api.get_card_set(
                revisable_only=True,
                include_markers=[tag]
            )
            priority = 0
            for card in revisable:
                if card.date_updated:
                    priority += (datetime.now() - card.date_updated).days
                else:
                    priority += (datetime.now() - card.date_created).days
            if len(total) != 0:
                priority = round(priority / len(total))
            if priority not in sorted_by_priority:
                sorted_by_priority[priority] = []
            sorted_by_priority[priority].append(tag)

        what = tags_groups_names[index]
        if sorted_by_priority != {}:
            tags = ', '.join(sorted_by_priority[
                max([val for i, val in enumerate(sorted_by_priority)])
            ])
            click.secho(
                'Revise {}: {}.'.format(what, tags),
                fg='yellow', bold=True
            )
        else:
            click.secho(
                'Revise {}: nothing to revise.'.format(what),
                fg='red', bold=True
            )

@main.command()
@click.option(
    '--inc', 'include_markers', type=str,
    help='A list of markers all of which each card that is to be affected must \
have. Examples: --inc=python; --inc="english,vocabulary"'
)
@click.option(
    '--exc', 'exclude_markers', type=str,
    help='A list of markers none of which each card that is to be affected must \
have. Examples: --exc=python; --exc="english,vocabulary"'
)
@click.option(
    '--add', 'add_marker', type=str,
    help='A marker to be added to all selected cards.'
)
@click.option(
    '--rem', 'remove_marker', type=str,
    help='A marker to be removed from all selected cards.'
)
def mass_tag_assign(include_markers, exclude_markers, add_marker, remove_marker):
    """
    [WIP] Mass assign of tags.
    """
    if include_markers is not None:
        include_markers = include_markers.split(',')
    else:
        include_markers = []
    if exclude_markers is not None:
        exclude_markers = exclude_markers.split(',')
    else:
        exclude_markers = []

    # fetch cards from the DB according to the constraints defined by input args
    card_set = api.get_card_set(
        include_markers=include_markers,
        exclude_markers=exclude_markers
    )

    if add_marker is not None:
        for card in card_set:
            card = card._replace(markers=card.markers + ' ' + add_marker)
            api.update_card(card, update_now=False)

    if remove_marker is not None:
        for card in card_set:
            markers = card.markers
            i = markers.find(remove_marker)
            ilen = i + len(remove_marker)
            if ' ' + remove_marker + ' ' in markers:
                markers = markers[0:i] + markers[ilen + 1:len(markers)]
            elif remove_marker in markers and ilen == len(markers):
                markers = markers[0:i]
            elif remove_marker in markers and i == 0:
                markers = markers[ilen + 1:len(markers)]
            card = card._replace(markers=markers)
            api.update_card(card, update_now=False)
