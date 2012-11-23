from raggregate.models import DBSession
from raggregate.models.user import User
from raggregate.models.vote import Vote
from raggregate.models.submission import Submission
from raggregate.models.comment import Comment
from raggregate.models.epistle import Epistle
from raggregate.models.stat import Stat
from raggregate.models.ban import Ban
from raggregate.queries import general
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
import sqlalchemy

import sqlahelper

from beaker import cache

import uuid
import os

from raggregate.login_adapters import LoginAdapterExc

from datetime import datetime
from datetime import timedelta
import calendar

import math

import json

import time

import pytz

dbsession = sqlahelper.get_session()

def calc_hot_average(hot_point_window = timedelta(hours = 6)):
    """
    Calculate the average point assignment of stories over the last hot_point_window time.
    """
    story_votes = dbsession.query(Vote.submission_id, func.sum(Vote.points).label('points')).filter(Vote.added_on < general.now_in_utc() and Vote.added_on > (general.now_in_utc() - hot_point_window)).group_by(Vote.submission_id).all()

    aggregate = 0
    count = 0

    for sv in story_votes:
        aggregate += sv.points
        count += 1

    print "aggregate: " + str(aggregate)
    print "count: " + str(count)

    if aggregate <= 0:
        hot_avg = 0
    else:
        # @TODO: this floating point division is basically extraneous
        # but I want it to look like something is happening for now
        # someone who cares about performance might want to remove this
        # especially since we are just creating an integer further down
        # if this is >= 1, which it will be in most sites.
        # especially since decimal comparison is meaningless here; < 1 = 0
        # users only vote in integers
        hot_avg = float(aggregate) / float(count)

    if hot_avg >= 1.0:
        hot_avg = math.floor(hot_avg)

    general.set_key_in_stat('hot_avg', hot_avg)
    general.set_key_in_stat('hot_avg_timestamp', general.now_in_utc(), type = 'datetime')

    print("hot_avg: {0}".format(hot_avg))

    return hot_avg

def calc_hot_window_score(submission_id, hot_point_window = timedelta(hours = 6)):
    """
    Retrieve vote/score information for a given submission over hot_point_window time.
    Count votes received in the last hot_point_window time. If this is higher than normal,
    the story will be considered hot.

    @param submission_id: the submission to calculate
    @param hot_point_window: timedelta object representing acceptable vote timeframe from now
    """
    try:
        story_votes = dbsession.query(Vote.submission_id, func.sum(Vote.points).label('points')).filter(Vote.added_on < general.now_in_utc() and Vote.added_on > (general.now_in_utc() - hot_point_window)).filter(Vote.submission_id == submission_id).group_by(Vote.submission_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        # no votes on this story yet
        return 0
    from raggregate.queries import submission
    story = submission.get_story_by_id(submission_id)
    story.hot_window_score = story_votes.points
    story.hot_window_score_timestamp = general.now_in_utc()
    dbsession.add(story)
    return story_votes.points

def calc_all_hot_window_scores(hot_eligible_age = timedelta(hours = 48)):
    # by default, only stories from the last 48 hours are eligible for "hot" status
    stories = dbsession.query(Submission).filter(Submission.deleted == False).filter(Submission.added_on > (general.now_in_utc() - hot_eligible_age)).all()

    for s in stories:
        calc_hot_window_score(s.id)

    general.set_key_in_stat('mass_hot_window_timestamp', general.now_in_utc(), type = 'datetime')

    dbsession.flush()

    return 0

def recentize_hots(hot_recalc_threshold = timedelta(hours = 1), hot_point_window = None, hot_eligible_age = None):
    """
    Recalculate the hot page every hot_recalc_threshold time.
    This depends on the timestamp keys placed in Stat in other calls.
    """

    count = 0
    def call_hot_average():
        if hot_point_window:
            calc_hot_average(hot_point_window)
        else:
            calc_hot_average()

    def get_hot_avg_time():
        hot_avg_timestamp = None

        try:
            hot_avg_timestamp = general.get_key_from_stat('hot_avg_timestamp', type = 'datetime')
        except sqlalchemy.orm.exc.NoResultFound:
            call_hot_average()

        if type(hot_avg_timestamp) == dict:
            return hot_avg_timestamp['value']
        else:
            return None

    hot_avg_timestamp = None

    while hot_avg_timestamp == None and count < 5:
        hot_avg_timestamp = get_hot_avg_time()
        count += 1

    if count >= 5:
        print("\t-----WARNING WARNING WARNING-----\n\tSomething has gone tragically wrong with the hotness: AVG.\n\t-----WARNING WARNING WARNING-----")

    hot_avg_timestamp = hot_avg_timestamp.replace(tzinfo=pytz.utc)

    if hot_avg_timestamp < (general.now_in_utc() - hot_recalc_threshold):
        call_hot_average()

    count = 0

    def call_all_hot_window_scores():
        if hot_eligible_age:
            calc_all_hot_window_scores(hot_eligible_age)
        else:
            calc_all_hot_window_scores()

    def get_mass_time():
        mass_timestamp = None

        try:
            mass_timestamp = general.get_key_from_stat('mass_hot_window_timestamp', type = 'datetime')
        except sqlalchemy.orm.exc.NoResultFound:
            call_all_hot_window_scores()

        if type(mass_timestamp) == dict:
            return mass_timestamp['value']
        else:
            return None

    mass_timestamp = None

    while mass_timestamp == None and count < 5:
        mass_timestamp = get_mass_time()
        count += 1

    if count >= 5:
        print("\t-----WARNING WARNING WARNING-----\n\tSomething has gone tragically wrong with the hotness: MASS.\n\t-----WARNING WARNING WARNING-----")

    mass_timestamp = mass_timestamp.replace(tzinfo=pytz.utc)

    if mass_timestamp < (general.now_in_utc() - hot_recalc_threshold):
        call_all_hot_window_scores()

    return 0

def get_hot_stories(hot_eligible_age = timedelta(hours = 48)):
    """
    Get a story list that is suitable for display as "hot".
    @param timediff: timedelta object representing hot story eligibility age
    """
    hot_avg = general.get_key_from_stat('hot_avg')['value']
    stories = dbsession.query(Submission).options(joinedload('submitter')).filter(Submission.deleted == False).filter(Submission.added_on > (general.now_in_utc() - hot_eligible_age)).filter(Submission.hot_window_score > hot_avg).order_by(Submission.hot_window_score.desc())
    return stories

def get_controversial_stories(timediff = timedelta(hours = 48), contro_threshold = 5, contro_min = 10):
    """
    Get a story list that is suitable for display as "controversial".
    @param timediff: timedelta representing controversial eligibility age
    @param contro_threshold: the maximum difference between up and down votes to be considered "controversial"
    @param contro_min: the minimum number of points required for something to appear as controversial
    @return: SA query ready to get list of stuff
    """
    stories = dbsession.query(Submission).options(joinedload('submitter')).filter(Submission.deleted == False).filter(Submission.added_on > (general.now_in_utc() - timediff)).filter(func.abs(Submission.upvote_tally - Submission.downvote_tally) <= contro_threshold).filter(Submission.total_vote_tally > contro_min).order_by(Submission.added_on.desc())
    return stories

def count_story_votes(submission_id):
    from raggregate.queries import submission
    dv_num = dbsession.query(Vote).filter(Vote.points < 0).filter(Vote.submission_id == submission_id).count()
    story = submission.get_story_by_id(submission_id)
    story.downvote_tally = dv_num
    story.downvote_tally_timestamp = general.now_in_utc()

    uv_num = dbsession.query(Vote).filter(Vote.points > 0).filter(Vote.submission_id == submission_id).count()
    story.upvote_tally = uv_num
    story.upvote_tally_timestamp = general.now_in_utc()

    story.total_vote_tally = uv_num + dv_num
    story.total_vote_timestamp = general.now_in_utc()

    dbsession.add(story)
    dbsession.flush()

    return [dv_num, uv_num]

def recentize_contro(recalc_timediff = timedelta(seconds = 1), age_timediff = timedelta(hours = 48)):
    """
    Ensure that upvote and downvote tallies of stories added in the last age_timediff time
    are no older than recalc_timediff time. Recalculate if so, do nothing if not.
    """
    stories = dbsession.query(Submission).filter(Submission.deleted == False).filter(Submission.added_on > (general.now_in_utc() - age_timediff)).filter(sqlalchemy.or_(sqlalchemy.or_(Submission.upvote_tally_timestamp < (general.now_in_utc() - recalc_timediff), Submission.downvote_tally_timestamp < (general.now_in_utc() - recalc_timediff)), sqlalchemy.or_(Submission.upvote_tally_timestamp == None, Submission.downvote_tally_timestamp == None))).all()
    for s in stories:
        count_story_votes(s.id)

    return 0

