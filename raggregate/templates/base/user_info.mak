<%inherit file="base.mak"/>

% if edit_mode:
    <form method="POST" action="/user_info?user_id=${u.id}" enctype="multipart/form-data">
        <ul class="form-list">
            <li>
                <label class="form-label" for="about-me">About Me</label>
                <textarea id="about-me" name="about_me" cols="50" rows="10">${u.about_me | template_filters.none_as_blank}</textarea>
            </li>
            <li>
                <label class="form-label" for="my-picture">My Picture</label>
                <input id="my-picture" type="file" name="picture" />
            </li>
            <li>
                <label class="form-label" for="email-address">Email</label>
                <input id="email-address" type="text" name="email" value="${u.email | template_filters.none_as_blank}" />
            </li>
        </ul>
        <input type="submit" value="Update" />
    </form>
    <br />
    <div id="change_pass_form">
        <b>Change Password for ${u.display_name()}</b>
        <form action="${request.route_url('login', _query=[('act', 'update_pw'), ('user_id', u.id)])}" method="POST">
            <ul class="form-list">
                <li>
                    <label class="form-label" for="old-password">Old Password</label>
                    <input id="old-password" name="old_password" type="password">
                </li>
                <li>
                    <label class="form-label" for="new-password">New Password</label>
                    <input id="new-password" name="new_password" type="password">
                </li>
                <li>
                    <label class="form-label" for="confirm-new-password">Confirm New Password</label>
                    <input id="confirm-new-password" name="new_password_confirm" type="password">
                </li>
            </ul>
            <input type="submit" value="Update Password" />
        </form>
    </div>

    <h2>Preferences</h2>
    <form id="preferences-form" action="/user_preferences" method="post">
        <ul class="form-list">
            <li>
                <label class="form-label" for="prop-link-directly-to-story">Title Links Directly to Story</label>
                <input id="prop-link-directly-to-story" name="prop-link-directly-to-story" type="checkbox" ${'checked' if link_to_story == 'on' else ''} />
            </li>
            <li>
                <label class="form-label" for="prop-auto-register-for-notifications">Automatically Register For Notifications</label>
                <%
                check_notify = None
                sett = request.registry.settings
                reg_def_name = 'site.register_notify_by_default'
                if reg_def_name in sett and sett[reg_def_name] == 'true':
                    check_notify = True
                if reg_for_notifications == 'off':
                    check_notify = False
                elif reg_for_notifications == 'on':
                    check_notify = True
                %>
                <input id="prop-auto-reg-for-notifications" name="prop-auto-reg-for-notifications" type="checkbox" ${'checked' if check_notify else ''} />
            </li>
        </ul>
        <input id="prop-submission" name="prop-submission" type="hidden" value="true" />
        <input type="submit" value="Update Preferences" />
    </form>
% endif

<h3>${u.display_name()}</h3>
% if u.picture:
    Picture: <img src="/user_imgs/${u.picture_ref.filename}" /><br />
% else:
    Picture: None uploaded yet<br />
% endif
    <br />
About Me: ${u.about_me | template_filters.render_md,n}
    <br />

<h3>Send a Message</h3>
<form method="post" action="/messages/out" id="reply-form">
    <ul class="form-list">
        <li>
            <label class="form-label" for="msg-subject">Subject</label>
            <input id="msg-subject" type="text" name="subject" />
        </li>
        <li>
            <label class="form-label" for="msg-body">Message</label>
            <textarea id="msg-body" name="body" cols="50" rows="10"></textarea>
        </li>
        <li>
            <label class="form-label" for="new-message-to">Message Recipient</label>
            <span id="new-message-to">${u.display_name()}</span><br />
            <input type="hidden" name="recipient" id="recipient-hidden" value="${u.id}" /><br />
        </li>
    </ul>
    <input type="submit" value="Send Message"></input>
</form>

<h2>Activity</h2>
            ##<h3>Comments</h3>
            ##% for c in u.comments:
            ##    Comment on <a href=${request.route_url('full', sub_id=c.parent_id)}>${c.load_parent().title}</a>: <br />
            ##    ${c.body} <br />
            ##    <br />
            ##% endfor
            <h3>Submissions</h3>
            % for s in u.submissions:
                Submitted <a href=${request.route_url('full', sub_id=s.id)}>${s.title}</a><br />
                <br />
            % endfor
            </div>

