<%inherit file="atom_base.mak" />

## @TODO: split story feed items and comment feed items into separate Mako
## templates for easy plugging, like extant templates story_item.mak and comment_item.mak

% for i in interleaved:
    <%
        type_flag = None

        # objects must be comments or stories
        # the body attr is exclusive to comment type
        # if we don't have it on the object, assume a story
        try:
            getattr(i, 'body')
            type_flag = "c"
        except:
            type_flag = "s"
    %>
    % if type_flag == "s":
        <entry>
            <title>${i.title}</title>
            <author>
                <name>${i.submitter.display_name()}</name>
            </author>
            <link href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(i))}" />
            <id>urn:uuid:${i.id}</id>
            <updated>${i.added_on.isoformat()}</updated>
            <summary>${i.description}</summary>
        </entry>
    % endif
    % if type_flag == "c":
        <% s = i.load_submission() %>
        <entry>
            <title>${i.submitter.display_name()} on ${s.title} (${fuzzify_date(i.added_on)})</title>
            <author>
                <name>${i.submitter.display_name()}</name>
            </author>
            <link href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(i.submission_id), _query=[('comment_perma', i.id)])}" />
            <id>urn:uuid:${i.id}</id>
            <updated>${i.added_on.isoformat()}</updated>
            <summary>${i.body}</summary>
        </entry>
    % endif
% endfor

