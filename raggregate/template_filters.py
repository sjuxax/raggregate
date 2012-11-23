import markdown
import queries

from raggregate.queries import submission

from raggregate.models.submission import Submission

md = markdown.Markdown( safe_mode='escape', )

def render_md(s):
    if s:
        return md.convert(s)
    else:
        return ""

def none_as_blank(s):
    """ Make it simple to display empty values as None. """
    if s == '' or s == 'None':
        return ""
    else:
        return s

def get_submission_identifier_for_url(s):
    if s.__class__ != Submission:
        s = submission.get_story_by_id(s)
    if s.slug is None or s.slug == '':
        return s.id
    else:
        return s.slug
