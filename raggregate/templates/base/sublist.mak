<%inherit file="base.mak"/>
    % if hasattr(sublist, 'title'):
        <i> showing sublist <b>${sublist.title}</b> </i>&nbsp;
        <br />
    % else:
        <form method="POST" action="${request.route_url('sublistc')}">
            Title: <input type="text" name="title" /><br />
            Desc: <input type="text" name="description" /><br />
            Visibility: <input type="text" name="visibility" /><br />
            <input type="submit" value="Add sublist" />
        </form>
    % endif
    % if len(stories) <= 0:
        <i>nothing to see here</i>
    % endif
    % if hasattr(sublist, 'added_by') and str(request.session['users.id']) == str(sublist.added_by):
        <form method="POST" action="${request.route_url('sublist', sub_title = sublist.title)}">
            Add members:<br />
            <textarea name="new_members" rows="20" cols="50"></textarea><br />
            <input type="submit" value="Add members" />
        </form>
    % endif
    % for s in stories:
        <%include file="story_item.mak" args="story_obj = s, vote_dict = vote_dict" />
        <br />
        % if hasattr(sublist, 'added_by') and str(request.session['users.id']) == str(sublist.added_by):
            <form method="GET" action="${request.current_route_url()}">
                <input type="hidden" value="${s.id}" name="sid" />
                <input type="hidden" value="del" name="op" />

                <input type="submit" value="Remove from Sublist"/><br />
            </form>
        % endif
    % endfor
    % if next_page:
        <br />
        % if filtered_section and filtered_section != 'all':
            <a href="${request.route_url('list', _query = [('page_num', next_page), ('sort', sort), ('section', filtered_section.name)])}">next page &rarr;</a>
        % else:
            <a href="${request.route_url('list', _query = [('page_num', next_page), ('sort', sort)])}">next page &rarr;</a>
        % endif
    % endif
    % if prev_page:
        <br />
        % if filtered_section:
            <a href="${request.route_url('list', _query = [('page_num', prev_page), ('sort', sort), ('section', filtered_section.name)])}">prev page &larr;</a>
        % else:
            <a href="${request.route_url('list', _query = [('page_num', prev_page), ('sort', sort)])}">prev page &larr;</a>
        % endif
    % endif
<br />
% if motd:
    Message of the day: <br />
    % if motd.link:
        <li>${motd.message} - ${motd.author} (<a href="${motd.link}">${motd.source}</a>, ${motd.datestring})</li>
    % else:
        <li>${motd.message} - ${motd.author} (${motd.source}, ${motd.datestring})</li>
    % endif
<br />
%endif
