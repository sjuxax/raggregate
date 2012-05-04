<%
s = pageargs['story_obj']
vote_dict = pageargs['vote_dict']
%>

              <div class="story-item" id="${s.id}">
                <%include file="vote_form.mak" args="id=s.id, direction='up', target='submission', jump_to=request.url"/>
                <%include file="vote_form.mak" args="id=s.id, direction='down', target='submission', jump_to=request.url"/>
                <div class="story-controls">
                    % if s.id in vote_dict and 1 in vote_dict[s.id]:
                        <div class="story-upvote logged-in-only active-vote"> <img id="upim-${s.id}" src="${static_base}images/arrow-up-active.png" style="padding-bottom: 2px;" /> </div>
                    % else:
                        <div class="story-upvote logged-in-only"> <img id="upim-${s.id}" src="${static_base}images/arrow-up-inactive.png" style="padding-bottom: 2px;" /> </div>
                    % endif
                    <div class="story-score" id="score-${s.id}"> ${s.points} </div>
                    % if s.id in vote_dict and -1 in vote_dict[s.id]:
                        <div class="story-downvote logged-in-only active-vote"> <img id="downim-${s.id}" src="${static_base}images/arrow-down-active.png" style="padding-top: 2px;" /> </div>
                    % else:
                        <div class="story-downvote logged-in-only"> <img id="downim-${s.id}" src="${static_base}images/arrow-down-inactive.png" style="padding-top: 2px;" /> </div>
                    % endif
                </div>
                <div class="story-thumb">
                </div>
                <div class="story-links">
                    % if s.self_post == True:
                    <span class="title"><a href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(s))}">${s.title}</a></span> <span class="domain">(self)</span> <br />
                    ## on the story list page, take users to the comments section instead of the direct url.
                    ## this template is used on other pages to take users directly to the URL, so we have to special case.
                    % elif request.route_url('post') in request.url or request.route_url('home') == request.url:
                    <span class="title"><a href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(s))}">${s.title}</a></span> <span class="domain">(${s.get_domain_name()})</span> <br />
                    % else:
                        <span class="title"><a href="${s.url}">${s.title}</a></span> <span class="domain">(${s.get_domain_name()})</span>&nbsp;<img src="${static_base}images/small-globe.png" />
                        % if s.url[-4:].lower() == ".pdf":
                            <b>[PDF]</b>
                        % endif
                        <br />
                    % endif
                    submitted ${fuzzify_date(s.added_on)} by <a href="${request.route_url('user_info', _query=[('user_id', s.submitter.id)])}">${s.submitter.display_name()}</a><br />
                    ## @TODO: this probably runs inefficiently.
                    ## We could supply a dictionary of sections to
                    ## this template from the controller and reference
                    ## that. Or do something else to make it fast.
                    in section ${s.sections.name}<br />
                    <%
                        saved_term = 'save'
                        if u and s in u.saved:
                            saved_term = 'unsave'
                    %>
                    <a href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(s))}">${s.comment_tally} comments</a> &nbsp;
                    % if logged_in:
                        | &nbsp; <a href="javascript:void(0)" class="save-link" id="save-${s.id}">${saved_term}</a>
                    % endif
                    % if str(s.submitter.id) == request.session['users.id'] or logged_in_admin:
                        &nbsp; | &nbsp; <a href="${request.route_url('post', _query=[('op', 'del'), ('sub_id', str(s.id))])}">delete</a>
                    % endif
                    <br />
                    % if request.route_url('full', sub_id = template_filters.get_submission_identifier_for_url(s)) in request.url:
                        <a href="http://twitter.com/share" data-text="${s.title} - ${site_name}: " data-url="${request.route_url('full', sub_id=str(template_filters.get_submission_identifier_for_url(s)))}" class="twitter-share-button" style="margin-top: 5px;">Tweet</a>
                    % endif
                </div>
            </div>
            <br />

