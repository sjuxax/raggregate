from raggregate.models.submission import Submission
from raggregate.models.user import User
from raggregate.models.comment import Comment
from raggregate.models.notify import Notify
from raggregate.queries import submission as submission_queries
from raggregate.queries import users as user_queries
from raggregate.queries import general

import sqlalchemy
import sqlahelper

import pyramid

dbsession = sqlahelper.get_session()

def get_notify_by_user_id(id):
    # Returns a list of notification objects filtered by user id
    return dbsession.query(Notify).filter(Notify.user_id == id).all()

def get_notify_by_id(id):
    return dbsession.query(Notify).filter(Notify.id == id).one()

def send_mail(user, submitter, submission, new_id, request):
    import smtplib
    from email.mime.text import MIMEText

    settings = request.registry.settings

    site_name = settings['site.site_name']
    from_mail = settings['site.notify_from']

    title = submission.title
    url = request.route_url('full', sub_id = submission.id,
                                _query=[('comment_perma', new_id)])
    unsubscribe_url = request.route_url('notify',
                                _query={'op':'del', 'target_id': new_id})
    username = user.name
    to = user.email

    # stop if the user doens't have an email
    # and pretend all is well.
    if not to:
        return True

    body = """Hi {display_name},

    {submitter} has sent you a reply!
    See it here: {url}

    Cordially,
    {site_name}

    To unsubscribe, click here: {unsubscribe_url}
    """.format(
                username = username,
                submitter = submitter,
                url = url,
                site_name = site_name,
                unsubscribe_url = unsubscribe_url
            )

    msg = MIMEText(body)
    msg['Subject'] = "{0}: new reply [{1}]".format(site_name, title)
    msg['From'] = from_mail
    msg['To'] = to

    s = smtplib.SMTP(settings['site.notify_mail_server'])
    s.sendmail(from_mail, [to], msg.as_string())
    return True

def get_users_to_notify(parent_id):
    """
    Returns real user objects.
    """
    res = dbsession.query(Notify).filter(Notify.target_id == parent_id).all()
    users = []
    [users.append(user_queries.get_user_by_id(x.user_id)) for x in res]
    return users

def is_user_notified(user_id, target_id):
    res = dbsession.query(Notify).filter(Notify.target_id == target_id)
    res = res.filter(Notify.user_id == user_id)
    try:
        r = res.all()[0]
        return r
    except:
        return False

def fire_to_listeners(parent_id, submitter, new_id, request):
    parent = general.find_by_id(parent_id)
    if isinstance(parent, Submission):
        submission = parent
    if isinstance(parent, Comment):
        submission = submission_queries.get_story_by_id(parent.submission_id)

    submitter = user_queries.get_user_by_id(submitter).display_name()

    users = get_users_to_notify(parent_id)
    for recipient in users:
        if 'users.id' in request.session and str(recipient.id) == request.session['users.id']:
            continue

        if recipient.notify_by_mail:
            send_mail(recipient, submitter, submission, new_id, request)

    return True

def create_notify(user_id, target_id, added_by, target_type = None):
    r = is_user_notified(user_id, target_id)
    if r:
        return r.id
    if not target_type:
        target_type = general.find_by_id(target_id).__class__.__name__.lower()
    n = Notify(user_id = user_id, target_id = target_id, target_type = target_type,
                added_by = added_by)
    dbsession.add(n)
    dbsession.flush()
    return n.id

def delete_notify(notify_id = None, user_id = None, target_id = None):
    if user_id and target_id and not notify_id:
        notify_id = is_user_notified(user_id, target_id).id
    dbsession.delete(get_notify_by_id(notify_id))
    dbsession.flush()
    return True
