<%inherit file="atom_base.mak" />

<%block name="feed_metadata">
<%
    site_name = request.registry.settings['site.site_name']
    feed_title = "{0} comments".format(site_name)
    feed_subtitle = "newest comments on {0}".format(site_name)
%>

        <title>${feed_title}</title>
        <subtitle>${feed_subtitle}</subtitle>
        <link href="${request.route_url(route)}" rel="self" />
        <id>${feed_title}+${feed_subtitle}+${site_name}</id>
</%block>

% for c in comments:
    <% s = c.load_submission() %>
    <entry>
        <title>${c.submitter.display_name()} on ${s.title} (${fuzzify_date(c.added_on)})</title>
        <author>
            <name>${c.submitter.display_name()}</name>
        </author>
        <link href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(c.submission_id), _query=[('comment_perma', c.id)])}" />
        <id>urn:uuid:${c.id}</id>
        <updated>${c.added_on.isoformat()}</updated>
        <summary>${c.body}</summary>
    </entry>
% endfor

