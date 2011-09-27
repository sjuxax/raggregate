import markdown
import queries

md = markdown.Markdown( safe_mode='escape', )

def render_md(s):
    if s:
        return queries.strip_p_tags(md.convert(s))
    else:
        return ""
