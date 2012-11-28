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
