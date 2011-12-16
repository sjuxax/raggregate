<%
    c = pageargs['comment']
    margin = pageargs['margin']
    if 'vote_dict' in pageargs:
        vote_dict = pageargs['vote_dict']
    else:
        vote_dict = None

    up_active_vote_str = ''
    down_active_vote_str = ''

    up_arrow_src = 'med-arrow-up-inactive.png'
    down_arrow_src = 'med-arrow-down-inactive.png'

    if c.id in vote_dict:
        if 1 in vote_dict[c.id]:
            up_active_vote_str = 'active-vote'
            up_arrow_src = 'med-arrow-up-active.png'
        if -1 in vote_dict[c.id]:
            down_active_vote_str = 'active-vote'
            down_arrow_src = 'med-arrow-down-active.png'

    comment_perma = None
    if 'comment_perma' in request.session['safe_params']:
        comment_perma = request.session['safe_params']['comment_perma']

%>
            % if comment_perma and comment_perma == str(c.id):
                <b>this is only one thread from this submission. click <a href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(c.submission_id))}">here</a> to see all the commentary.</b><br />
                <div class="comment" id="${c.id}" style="margin-left: ${margin}px; background-color: #fffdc9 ! important;">
            % else:
                <div class="comment" id="${c.id}" style="margin-left: ${margin}px;">
            % endif
                    <a name="${c.id}" id="${c.id}-anchor" />
                    <div class="comment-votes-picture">
<%
# leave this indentation this way please
if c.submitter.picture_ref:
    u_pic = c.submitter.picture_ref.filename
else:
    u_pic = "qmark.png"
%>
                    <img src="${static_base}images/${up_arrow_src}" id="upim-${c.id}" class="comment-upvote logged-in-only ${up_active_vote_str}" /><br />
                    <span id="score-${c.id}" class="comment-score">${c.points}</span> <br />
                    <img src="${static_base}images/${down_arrow_src}" id="downim-${c.id}" class="comment-downvote logged-in-only ${down_active_vote_str}" /><br />
                </div>
                <div class="comment-content">
                    <%
                    followed_class = ''
                    followed_term = 'follow'
                    followed_op = 'add'
                    if c.submitter.id in followed_users:
                        followed_class = 'follows'
                        followed_term = 'unfollow'
                        followed_op = 'del'
                    %>
                    <span class="comment-heading"><span class="comment-username ${followed_class}"><a href="${request.route_url('user_info', _query=[('user_id', c.submitter.id)])}">${c.submitter.display_name()}</a></span> ${fuzzify_date(c.added_on)} </span>
                    <br />
                    ## <span class="c-body-text" id="body-${c.id}">${c.body.replace("\n", "<br />\n") | n}</span>
                    <div class="c-body-text" id="body-${c.id}">${c.body | template_filters.render_md,n}</div>
                    <div class="comment-controls">
                    <a href="#comment" id="reply-${c.id}" class="comment-reply logged-in-only">reply</a> &nbsp;  <a href="javascript:void(0)" class="follow-link logged-in-only" data-submitter-id="${c.submitter.id}" id="follow-${c.submitter.id}">${followed_term}</a> &nbsp; <a href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(c.submission_id), _query=[('comment_perma', c.id)])}">permalink</a>
                    % if str(c.submitter.id) == request.session['users.id'] or logged_in_admin:
                        &nbsp; <a href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(c.submission_id), _query=[('op', 'del'), ('comment_id', str(c.id))])}">delete</a>
                    % endif
                    % if str(c.submitter.id) == request.session['users.id'] or logged_in_admin:
                        &nbsp; <a href="javascript:void(0)" data-comment-id="${c.id}" class="comment-edit-link">edit</a>
                        <div class="c-body-md" style="display: none;" id="body-md-${c.id}">${c.body | h}</div>
                    % endif
                    </div>
                    <%include file="vote_form.mak" args="id=c.id, direction='up', target='comment', jump_to=request.url"/>
                    <%include file="vote_form.mak" args="id=c.id, direction='down', target='comment', jump_to=request.url"/>
                </div>
            </div>
