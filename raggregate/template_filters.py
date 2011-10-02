import markdown
import queries

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
