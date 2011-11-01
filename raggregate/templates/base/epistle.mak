<%inherit file="base.mak"/>
<script type="text/javascript">
$(document).ready(function() {
    nm = $('#new_message').detach();
    $('.reply-link').click( function(e) {
        nm.css('display', 'block');
        $($(e.target).closest('.message')).append(nm);
        $('#recipient-hidden').attr('value', $(e.target).attr('data-uid'));
        $('#parent_id-hidden').attr('value', $(e.target).attr('data-mid'));
        $('#new-message-to').text($(e.target).attr('data-display'));
    })
});
</script>

<style type="text/css">
    .message_subject { color: red; }
</style>

        <h2>Messages</h2>
        <a href="${request.route_url('epistle', box='in')}">unread</a> &nbsp;
        <a href="${request.route_url('epistle', box='read')}">in</a> &nbsp;
        <a href="${request.route_url('epistle', box='read')}">out</a> &nbsp;
        <br />
        <br />

		% for e_root in epistles['roots']:
            <div class="message">
                % if e_root.parent_type == 'story':
                    <i>left on <a href="/full/${e_root.parent_info.id}">${e_root.parent_info.title}</a></i><br />
                % elif e_root.parent_type == 'comment':
                    <i>in reply to ${e_root.parent_info.submitter.display_name()}'s comment</i><br />
                % elif e_root.parent_type == 'epistle':
                    <h2 class="message_subject">${e_root.display_subject()}</h2>
                % endif
                <%def name="print_replies(e)">
                    % if str(e.recipient_u.id) == request.session['users.id']:
                        <b>from <a href="${request.route_url('user_info', _query = [('user_id', e.sender_u.id)])}">${e.sender_u.display_name()}</a> sent ${fuzzify_date(e.added_on)}</b>
                    % else:
                        <b>to <a href="${request.route_url('user_info', _query = [('user_id', e.sender_u.id)])}">${e.recipient_u.display_name()}</a> sent ${fuzzify_date(e.added_on)}</b>
                    % endif
                    <div id="${e.id}">${e.body}</div>
                </%def>
                ${print_replies(e_root)}
                <br />
                % if str(e_root.id) in epistles['children']:
                    % for e in epistles['children'][str(e_root.id)]:
                        ${print_replies(e)}
                        <br />
                    % endfor
                % endif
                <a href="#" class="reply-link" data-mid="${e_root.id}" data-uid="${e_root.sender_u.id}" data-display="${e_root.sender_u.display_name()}">Reply</a><br />
           <hr />
           </div>
        % endfor
        % if len(epistles['roots']) < 1:
            no mail
        % endif
        <div id="new_message" style="display:none">
            <h3>Send a Message</h3>
            <form method="post" action="/messages/out" id="reply-form">
                Subject: <input type="text" name="subject" /><br />
                Message: <input type="textarea" name="body" /><br />
                To: <span id="new-message-to">-</span><br />
                <input type="hidden" name="recipient" id="recipient-hidden" /><br />
                <input type="hidden" name="parent_id" id="parent_id-hidden" /><br />
                <input type="submit" value="Send Message"></input>
            </form>
        </div>
