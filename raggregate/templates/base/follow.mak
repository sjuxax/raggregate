<%inherit file="base.mak"/>
        <h2>Followed Users</h2>
		% for u in follows:
            <h3>${u.display_name()}</h3>
            <div style="margin-left:10px;">
            % for s in u.submissions:
                <%include file="story_item.mak" args="story_obj = s, vote_dict = vote_dict" />
            % endfor
            </div>
        % endfor
