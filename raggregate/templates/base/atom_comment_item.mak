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
