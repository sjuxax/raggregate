<html>
    <head>
        <title><%block name="html_title">${site_name}</%block></title>
        <script type="text/javascript" src="${static_base}jquery-1.7.min.js"></script>
    </head>
    <style type="text/css">

        html { height: 100%; margin: 0px; padding: 0px; }

        body { margin-left: 12px;
               font-family: Arial; }

        iframe { width: 105px ! important; vertical-align: bottom; margin-top: 6px; }

        #logo_bar { width: 100%;
                    margin-top: 5px;
                    height: 50px; }

        .right_side_box { background-color: #dcf9ff;
                    text-align: center;
                    clear: right;
                    margin-top: 5px;
                    margin-right: 15px;
                    padding: 8px; }

        .big_username { color: black; font-size: 24px; }

        #sidebar { width: 20%; float: right; }

        #main_content { padding-top:12px;
                        width: 70%;
                        clear: both;
                        float: left; }

        #footer { clear: both;
                  text-align: center; }

    </style>

    <style type="text/css">
        .title a { color: blue; font-size: 1.1em; text-decoration:none; font-weight: bold; }
        .title a:visited { color: #aa00ff; }
        .domain { color: #999; font-size: 0.7em; }
        .story-controls { float: left; color: #cccccc; font-size: 24px; }
        .story-links { position: relative; left:15px; }
        .story-description { background-color: #f6f6f6; border: 1px black solid; padding: 3px; }
        .story-description p:last-child { margin-bottom: 0px; }
        .story-description p:first-child { margin-top: 0px; }
        .story-item { width: 600px; clear: both; }
        /* If the number of parent divs changes, this calculation must change too */
        /* The idea is to only apply this rule to .story-items after the first */
        /* But CSS doesn't support that filtering; it must be based on the number of parent divs */
        /* without regard to class. Someone should do this better. @FIXME */
        .story-item:nth-child(n+3) { margin-top: 30px; }
        .story-score { text-align: center; }
        .story-thumb { float: left; margin-left: 10px; }
    </style>

    <style type="text/css">
        .comment { width: 100%; overflow: hidden; margin-bottom: 5px; }
        .comment-votes-picture { float: left; padding-right: 6px; text-align: center; }
        .comment-content { float: left; margin-bottom: 7px; width: 60%; }
        .comment-content p:last-child { margin-bottom: 0px; }
        .comment-content p:first-child { margin-top: 0px; }
        .comment-username a:visited { color: #aa00ff; }
        .comment-username a { color: #0000dd; text-decoration:none; }
        .comment-controls { color: #cccccc; font-size: .85em; }
        .comment-heading { font-weight: normal; font-size: .8em; }
        .comment-score { color: #cccccc; font-weight: bold; }
        .comment-controls a { color: #888; text-decoration: none; }
        .c-body-text { margin-top: 3px; margin-bottom: 3px; }
        .follows a { color: #0000ff ! important; }
    </style>

    <script src="http://platform.twitter.com/widgets.js" type="text/javascript"></script>
% if logged_in:
    <script type="text/javascript">

        var active_down_src = "${static_base}/images/arrow-down-active.png"
        var down_src = "${static_base}/images/arrow-down-inactive.png"

        var active_up_src = "${static_base}/images/arrow-up-active.png"
        var up_src = "${static_base}/images/arrow-up-inactive.png"

        function update_score_display (score, diff, id) {
            score_int = parseInt(score);
            $("#score-" + story_id).text((score_int + diff));
            if (diff == 1) {
                $("#upim-" + story_id).attr('src', active_up_src);
                $($("#upim-" + story_id).parent()).addClass('active-vote');
                $($("#downim-" + story_id).parent()).removeClass('active-vote');
                $("#downim-" + story_id).attr('src', down_src);
            } else if (diff == -1) {
                $("#downim-" + story_id).attr('src', active_down_src);
                $($("#downim-" + story_id).parent()).addClass('active-vote');
                $($("#upim-" + story_id).parent()).removeClass('active-vote');
                $("#upim-" + story_id).attr('src', up_src);
            }
        }

        $(document).ready(
            function () {
                $('.story-upvote').click( function(e) {
                    if (!$(e.target).parent().hasClass('active-vote')) {
                        story_id = $($(e.target).closest('.story-item')).attr('id');
                        form_obj = $("#up-" + story_id)
                        $.post(form_obj.attr('action'), form_obj.serialize(),
                        update_score_display($('#score-' + story_id).text(), 1, story_id));
                    }
                });
                $('.story-downvote').click( function(e) {
                    if (!$(e.target).parent().hasClass('active-vote')) {
                        story_id = $($(e.target).closest('.story-item')).attr('id');
                        form_obj = $("#down-" + story_id)
                        $.post(form_obj.attr('action'), form_obj.serialize(),
                        update_score_display($('#score-' + story_id).text(), -1, story_id));
                    }
                });
            });
    </script>
    <script type="text/javascript">

        var active_comm_down_src = "${static_base}/images/med-arrow-down-active.png"
        var down_comm_src = "${static_base}/images/med-arrow-down-inactive.png"

        var active_comm_up_src = "${static_base}/images/med-arrow-up-active.png"
        var up_comm_src = "${static_base}/images/med-arrow-up-inactive.png"

        function update_comm_score_display (score, diff, comment_id) {
            score_int = parseInt(score);
            $("#score-" + comment_id).text((score_int + diff));
            if (diff == 1) {
                $("#upim-" + comment_id).attr('src', active_comm_up_src);
                $("#upim-" + comment_id).addClass('active-vote');
                $("#downim-" + comment_id).removeClass('active-vote');
                $("#downim-" + comment_id).attr('src', down_comm_src);
            } else if (diff == -1) {
                $("#downim-" + comment_id).attr('src', active_comm_down_src);
                $("#downim-" + comment_id).addClass('active-vote');
                $("#upim-" + comment_id).removeClass('active-vote');
                $("#upim-" + comment_id).attr('src', up_comm_src);
            }
        }

        $(document).ready(
            function () {
                $('.comment-upvote').click( function(e) {
                    if (!$(e.target).hasClass('active-vote')) {
                        comment_id = $($(e.target).closest('.comment')).attr('id');
                        form_obj = $("#up-" + comment_id)
                        $.post(form_obj.attr('action'), form_obj.serialize(),
                        update_comm_score_display($('#score-' + comment_id).text(), 1, comment_id));
                    }
                });
                $('.comment-downvote').click( function(e) {
                    if (!$(e.target).hasClass('active-vote')) {
                        comment_id = $($(e.target).closest('.comment')).attr('id');
                        form_obj = $("#down-" + comment_id)
                        $.post(form_obj.attr('action'), form_obj.serialize(),
                        update_comm_score_display($('#score-' + comment_id).text(), -1, comment_id));
                    }
                });
            });
    </script>

    <script type="text/javascript">
        $(document).ready(function() {
            $('.save-link').click( function(e) {
                var save_element = $('#' + $(e.target).attr('id'));
                if (save_element.text() == 'save') {
                    var save_url = '${request.route_url('save')}' + '?story_id=' + $(e.target).attr('id').replace('save-', '');
                    $.get(save_url, function() { save_element.text('unsave') });
                } else {
                    var save_url = '${request.route_url('save')}' + '?story_id=' + $(e.target).attr('id').replace('save-', '') + '&op=del';
                    $.get(save_url, function() { save_element.text('save') });
                }
            });
            $('.follow-link').click(function(e) {
                var follow_element = $('#' + $(e.target).attr('id'));
                follow_guid = follow_element.attr('id').replace('follow-', '');
                if (follow_element.text() == 'Follow') {
                    follow_url = '${request.route_url('follow', _query = [('jump_to', request.url), ('op', 'add')])}' + "&follow_id=" + follow_element.attr('id').replace('follow-', '');
                    $.get(follow_url, function() { $('a[data-submitter-id*="'+ follow_guid +'"]').text('Unfollow') });
                } else {
                     follow_url = '${request.route_url('follow', _query = [('jump_to', request.url), ('op', 'del')])}' + "&follow_id=" + follow_element.attr('id').replace('follow-', '');
                    $.get(follow_url, function() { $('a[data-submitter-id*="'+ follow_guid +'"]').text('Follow') });
                }
            });
        });
    </script>
% else:
    <script type="text/javascript">
        $(document).ready(function() {
            $('.logged-in-only').click( function() { alert("You must be logged in to do that.") } );
        });
    </script>
% endif
    <body>
        <div id="logo_bar">
            <a href="${request.route_url('post')}"><img src="${static_base}images/logo.png" style="border: 0" /></a>
        </div>

        % if success == False:
            % if 'message' in request.session:
                ${request.session['message']}<br />
            % endif
            % if code:
                Error Code: <b>${code}</b>
            % else:
                Error Code: <b>Unknown</b>, please report this to an admin
            % endif
            <% return %>
        % endif

        ## @TODO: mako offers things that make it so we don't have to special case like this
        ## we should use them some time
        % if request.route_url('post') in request.url or request.route_url('home') == request.url:

            <style type="text/css">
                #home_nav_links { margin-top: 9.5px; padding: 0px; float: left; }
                #home_nav_links li { display: inline; padding: 12px; }
                #home_nav_links li:hover { background-image: url('${static_base}images/active-arrow.png'); background-repeat: no-repeat; background-position: center bottom; }
                #home_nav_links a { text-decoration: none; color: black; }
                #search_form { float:right; margin-top: 5px; }
                .active { background-color: #e1e3e8; font-weight: bold; background-image: url('${static_base}images/active-arrow.png'); background-repeat: no-repeat; background-position: center bottom; }
            </style>

            <div id="home_nav">
                <ul id="home_nav_links">
                    <%def name="is_term_active(term)">
                    <%
                        if sort in request.params and term == request.params['sort']:
                            return 'active'
                        elif sort not in request.params and (request.url == request.route_url('post') or request.url == request.route_url('home') ) and term == 'new':
                            return 'active'
                        elif 'full' not in request.url and term in request.url:
                            return 'active'
                        else:
                            return ''
                    %>
                    </%def>
                    <li class="${is_term_active('new')}"><a href="${request.route_url('post', _query = [('sort', 'new'),])}">New</a></li>
                    <li class="${is_term_active('top')}"><a href="${request.route_url('post', _query = [('sort', 'top'),])}">Top</a></li>
                    <li class="${is_term_active('hot')}"><a href="${request.route_url('post', _query = [('sort', 'hot'),])}">Hot</a></li>
                    <li class="${is_term_active('contro')}"><a href="${request.route_url('post', _query = [('sort', 'contro'),])}">Controversial</a></li>
                    % if logged_in:
                        <li class="${is_term_active('save')}"><a href="${request.route_url('save',)}">Saved</a></li>
                        <li class="${is_term_active('follow')}"><a href="${request.route_url('follow')}">Followed</a></li>
                        <li class="${is_term_active('message')}">
                        % if new_message_num is not None:
                            <a href="${request.route_url('epistle', box='in')}">${new_message_num} new messages</a>
                        % else:
                            <a href="${request.route_url('epistle', box='read')}">Messages</a>
                        % endif
                    % endif
                    </li>

                </ul>
                <form id="search_form" action="/search" method="GET"><input type="text" name="term" value="Search Here" /></form>
            </div>

        % endif

        <div id="main_content">
            <div id="included">
                ${self.body()}
            </div>
        </div>
<div id="sidebar">
                <div id="user_box" class="right_side_box">
                <%
                if 'logged_in' in request.session and request.session['users.display_name'] == 'Unregistered User':
                    temp_user = True
                else:
                    temp_user = False
                %>
                % if 'logged_in' not in request.session or temp_user:
                    <h4>Register &amp; Login</h4>
                    % if temp_user and request.route_url('login') in request.url:
                        <a href="${request.route_url('login')}">Keep Temp Profile</a>&nbsp;
                    % endif
                    % if request.registry.settings['twitter.app_key'] != 'none' and request.registry.settings['twitter.app_secret'] != 'none':
                        <a href="${request.route_url('twit_sign')}"><img src="https://si0.twimg.com/images/dev/buttons/sign-in-with-twitter-l.png" /></a><br />
                    % endif
                    % if request.registry.settings['facebook.app_key'] != 'none' and request.registry.settings['facebook.app_secret'] != 'none':
                        <div id="fb-root"></div>
                        <fb:login-button autologoutlink="true"></fb:login-button><br />
                        <script>
                        window.fbAsyncInit = function() {
                            FB.init({appId: ${request.registry.settings['facebook.app_key']}, status: true, cookie: true,
                                xfbml: true});
                            FB.Event.subscribe('auth.login', function(response) {
                                    window.location.replace("/login");
                            });
                            FB.Event.subscribe('auth.logout', function(response) {
                                window.location.replace("/login?logout");
                            });
                            };
                            (function() {
                                var e = document.createElement('script');
                                e.type = 'text/javascript';
                            e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
                            e.async = true;
                                document.getElementById('fb-root').appendChild(e);
                            }());
                        </script>
                        <br />
                    % endif
                        <a href="${request.route_url('login')}">Login</a>&nbsp;
                % endif
                % if 'logged_in' in request.session and not temp_user:
                    <span class="big_username">${request.session['users.display_name']}</span><br />
                    % if new_message_num is not None:
                        <a href="${request.route_url('epistle', box='in')}">${new_message_num} new messages</a> <br />
                    % else:
                        <a href="${request.route_url('epistle', box='read')}">Messages</a> <br />
                    % endif
                    % if karma is not None:
                        Karma: <b>${karma}</b> <br />
                    % endif
                    <a href="${request.route_url('user_info')}">Edit Account</a> &dash; <a href="${request.route_url('login', _query=[('logout', '')])}">Logout</a>
                 % endif
           </div>
            <div class="right_side_box" id="submit_link">
                <h2><a href="${request.route_url('post', _query=[('new_post', 'y')])}">Submit a Link!</a></h2>
            </div>
            </div>

    </div>
        <br />
        <div id="footer">
            <br />
            <div id="footer_links"> <a href="#">About</a> &nbsp; <a href="#">FAQ</a> &nbsp; <a href="#">Contact Us</a> &nbsp; <a href="#">Privacy Policy</a> &nbsp; </div>
            <div id="footer_copy">&copy; 2011</div>
        </div>
    </div>
</body>
</html>
