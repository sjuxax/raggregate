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
                <input id="email-address"type="text" name="email" value="${u.email | template_filters.none_as_blank}" />
            </li>
        </ul>
        <input type="submit" value="Update" />
    </form>
    <br />
    <div id="change_pass_form">
        <b>Change Password for ${u.display_name()}</b>
        <form action="${request.route_url('login', _query=[('act', 'update_pw')])}" method="POST">
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
            <label class="form-label" for="msg-subject">New Password</label>
            <input id="msg-subject" type="text" name="subject" />
        </li>
        <li>
            <label class="form-label" for="msg-body">Message</label>
            <input id="msg-body" type="textarea" name="body" />
        </li>
        <li>
            <label class="form-label" for="new-message-to">Message</label>
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
