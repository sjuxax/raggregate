<%inherit file="base.mak"/>
    % if filtered_section and filtered_section != 'all':
        <i> showing section <b>${filtered_section.name}</b> </i>&nbsp;
        % if 'logged_in' in request.session:
            ##TODO: This doesn't work properly, still shows "Subscribed" when already subscribed
            % if filtered_section.id in subscribed_to_list:
                <a href="${request.route_url('list', _query = [('section', filtered_section.name), ('subscribe', 'n')])}">[unsubscribe]</a><br />
            % else:
                <a href="${request.route_url('list', _query = [('section', filtered_section.name), ('subscribe', 'y')])}">[subscribe]</a><br />
            % endif
        % endif
    % endif
    filter by section: <form action="${request.route_url('list')}" method="GET">
                           % if sort:
                                   <input type="hidden" name="sort" value="${sort}" />
                           % endif
                           <select name="section">
                               <option value="" ${"selected=\"selected\"" if not filtered_section else ""}>subscribed</option>
                               <option value="all" ${"selected=\"selected\"" if filtered_section == 'all' else ""}>all</option>
                               % for section in sections:
                                   % if filtered_section and filtered_section != 'all' and filtered_section.name == section.name:
                                       <option selected="selected">${section.name}</option>
                                   % else:
                                       <option>${section.name}</option>
                                   % endif
                               % endfor
                           </select> <input type="submit" value="Go" />
                       </form>
    % if len(stories) <= 0:
        <i>nothing to see here</i>
    % endif
    % for s in stories:
        <%include file="story_item.mak" args="story_obj = s, vote_dict = vote_dict" />
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
