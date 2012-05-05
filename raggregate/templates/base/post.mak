<%inherit file="base.mak"/>
       % if 'new_post' in context['request'].session['safe_get']:
            <form action="post" METHOD="POST">
                <b>${message}</b><br />
                Title: <input type="text" name="title" value="${new_title_text}" maxlength="100" /><br />
                <br />
                <b>At least one of these is required</b><br />
                Description: <textarea name="description" cols="50" rows="10"></textarea><br />
                URL: <input type="text" name="url" value="${new_url_text}" /><br />
                Section: <select name="section_id">
                    % for section in sections:
                        <option value="${section.id}">${section.name}</option>
                    % endfor
                </select><br />
                ##% if 'section_id' in request.session['safe_get']:
                ##    <input type="hidden" value="${request.session['safe_get']['section_id']}" name="section_id" />
                ##% endif
                <br />
                <input type="submit" value="Post Story" /><br />
            </form>
        % else:
            % if filtered_section:
                <i> showing section <b>${filtered_section.name}</b> </i><br />
            % endif
            filter by section: <form action="${request.route_url('post')}" method="GET">
                                   <select name="section">
                                       % for section in sections:
                                       <option value="">all</option>
                                       <option>${section.name}</option>
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
                <a href="${request.route_url('post', _query = [('page_num', next_page), ('sort', sort)])}">next page &rarr;</a>
            % endif
            % if prev_page:
                <br />
                <a href="${request.route_url('post', _query = [('page_num', prev_page), ('sort', sort)])}">prev page &larr;</a>
            % endif
        % endif
