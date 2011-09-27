<%inherit file="base.mak"/>
       % if 'new_post' in context['request'].GET:
            <form action="post" METHOD="POST">
                <b>${message}</b><br />
                Title: <input type="text" name="title" /><br />
                <br />
                <b>At least one of these is required</b><br />
                Description: <textarea name="description" cols="50" rows="10"></textarea><br />
                URL: <input type="text" name="url" /><br />
                <br />
                <input type="submit" value="Post Story" /><br />
            </form>
        % else:
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
