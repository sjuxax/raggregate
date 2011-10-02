<%
    c = pageargs['comment']
    margin = pageargs['margin']
    if 'vote_dict' in pageargs:
        vote_dict = pageargs['vote_dict']
    else:
        vote_dict = None

    up_active_vote_str = ''
    down_active_vote_str = ''

    up_arrow_src = 'sm-arrow-up-inactive.png'
    down_arrow_src = 'sm-arrow-down-inactive.png'

    if c.id in vote_dict:
        if 1 in vote_dict[c.id]:
            up_active_vote_str = 'active-vote'
            up_arrow_src = 'sm-arrow-up-active.png'
        if -1 in vote_dict[c.id]:
            down_active_vote_str = 'active-vote'
            down_arrow_src = 'sm-arrow-down-active.png'

%>          
            <div class="comment" id="${c.id}" style="margin-left: ${margin}px;">
                <div class="comment-picture">
<%
# leave this indentation this way please
if c.submitter.picture_ref:
    u_pic = c.submitter.picture_ref.filename
else:
    u_pic = "qmark.png"
%>
                </div>
                <div class="comment-content">
                    <%
                    followed_class = ''
                    followed_term = 'Follow'
                    followed_op = 'add'
                    if c.submitter.id in followed_users:
                        followed_class = 'follows'
                        followed_term = 'Unfollow'
                        followed_op = 'del'
                    %>
                    <span class="comment-heading"><span class="comment-username ${followed_class}"><a href="${request.route_url('user_info', _query=[('user_id', c.submitter.id)])}">${c.submitter.display_name()}</a></span> ${fuzzify_date(c.added_on)} </span>
                    <br />
                    ## <span class="c-body-text" id="body-${c.id}">${c.body.replace("\n", "<br />\n") | n}</span>
                    <div class="c-body-text" id="body-${c.id}">${c.body | template_filters.render_md,n}</div>
                    <div class="comment-controls">
                    <img src="${static_base}images/${up_arrow_src}" id="upim-${c.id}" class="comment-upvote logged-in-only ${up_active_vote_str}" /> <span id="score-${c.id}" class="comment-score">${c.points}</span> <img src="${static_base}images/${down_arrow_src}" id="downim-${c.id}" class="comment-downvote logged-in-only ${down_active_vote_str}" />&nbsp; <a href="#comment" id="reply-${c.id}" class="comment-reply logged-in-only">Reply</a> &nbsp;  <a href="javascript:void(0)" class="follow-link logged-in-only" data-submitter-id="${c.submitter.id}" id="follow-${c.submitter.id}">${followed_term}</a>
                    % if str(c.submitter.id) == request.session['users.id'] or logged_in_admin:
                        &nbsp; <a href="${request.route_url('full', sub_id = c.submission_id, _query=[('op', 'del'), ('comment_id', str(c.id))])}">delete</a>
                    % endif
                    % if str(c.submitter.id) == request.session['users.id'] or logged_in_admin:
                        &nbsp; <a href="javascript:void(0)" data-comment-id="${c.id}" class="comment-edit-link">edit</a>
                    % endif
                    </div>
                    <%include file="vote_form.mak" args="id=c.id, direction='up', target='comment', jump_to=request.url"/>
                    <%include file="vote_form.mak" args="id=c.id, direction='down', target='comment', jump_to=request.url"/>
                </div>
            </div>
