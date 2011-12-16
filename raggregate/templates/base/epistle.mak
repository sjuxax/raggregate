<%inherit file="base.mak"/>
<script type="text/javascript">
$(document).ready(function() {
    nm = $('#new_message').detach();
    $('.reply-link').click( function(e) {
        nm.css('display', 'block');
        $($(e.target).closest('.message')).append(nm);
        $('#recipient-hidden').attr('value', $(e.target).attr('data-uid'));
        $('#parent_id-hidden').attr('value', $(e.target).attr('data-mid'));
        $('#message-subject').css('display', 'none');
        $('#new-message-to').text($(e.target).attr('data-display'));
    })
    $('.your-comment-flyout').toggle( function(e) {
        var cid = $(e.target).attr('data-cid');
        $('#flyout-' + cid).css('display', 'block');
    }, function(e) {
        var cid = $(e.target).attr('data-cid');
        $('#flyout-' + cid).css('display', 'none');
    })
});
</script>

<style type="text/css">
    .message_subject { color: red; }
    .comment-flyout {margin: 5px; background-color:#F6F6F6; padding: 6px; width: 50%; }
</style>

        <h2>Messages</h2>
        <a href="${request.route_url('epistle', box='in')}">unread</a> &nbsp;
        <a href="${request.route_url('epistle', box='read')}">in</a> &nbsp;
        <a href="${request.route_url('epistle', box='out')}">out</a> &nbsp;
        <a href="${request.route_url('epistle', box='comments')}">last 20 replies to your comments</a> &nbsp;
        <br />
        <br />
                <%def name="print_replies(obj, sender_id, recipient_id, sender_display_name, recipient_display_name)">
                    % if str(recipient_id) == request.session['users.id']:
                        <b>from <a href="${request.route_url('user_info', _query = [('user_id', sender_id)])}">${sender_display_name}</a> sent ${fuzzify_date(obj.added_on)}</b>
                    % else:
                        <b>to <a href="${request.route_url('user_info', _query = [('user_id', sender_id)])}">${recipient_display_name}</a> sent ${fuzzify_date(obj.added_on)}</b>
                    % endif
                    <div id="${obj.id}">${obj.body | template_filters.render_md,n}</div>
                </%def>
        % for c in comments:
           <div class="message">
           % if isinstance(c.load_parent(), c.__class__):
               <i>in reply to <a href="#" class="your-comment-flyout" data-cid="${c.parent_id}">your comment</a> on <a href="${request.route_url('full', sub_id=c.submission_id)}">${c.load_submission().title}</a></i><br />
               <div id="flyout-${c.parent_id}" class="comment-flyout" style="display:none;">
                   ${c.load_parent().body}
               </div>
           % else:
                <i>in reply to <a href="${request.route_url('full', sub_id = c.load_parent().id)}">${c.load_parent().title}</a></i><br />
           % endif
               ${print_replies(c, c.submitter.id, c.recipient_u.id, c.submitter.display_name(), c.recipient_u.display_name(),)}
               <a href="#" class="reply-link" data-mid="${c.id}" data-uid="${c.submitter.id}" data-display="public -- will be posted as a comment">Reply</a><br />
               <br />
           </div>
        % endfor
		% for e_root in epistles['roots']:
            <div class="message">
                % if e_root.parent_type == 'story':
                    <i>left on <a href="/full/${e_root.parent_info.id}">${e_root.parent_info.title}</a></i><br />
                % elif e_root.parent_type == 'comment':
                    <i>in reply to ${e_root.parent_info.submitter.display_name()}'s comment</i><br />
                % elif e_root.parent_type == 'epistle' or e_root.parent_type == 'reply':
                    <h2 class="message_subject">${e_root.display_subject()}</h2>
                % endif
               ${print_replies(e_root, e_root.sender_u.id, e_root.recipient_u.id, e_root.sender_u.display_name(), e_root.recipient_u.display_name(),)}
                % if str(e_root.id) in epistles['children']:
                    % for e in epistles['children'][str(e_root.id)]:
                        ${print_replies(e, e.sender_u.id, e.recipient_u.id, e.sender_u.display_name(), e.recipient_u.display_name(),)}
                    % endfor
                % endif
                <a href="#" class="reply-link" data-mid="${e_root.id}" data-uid="${e_root.sender_u.id}" data-display="${e_root.sender_u.display_name()}">Reply</a><br />
           <hr />
           </div>
        % endfor
        % if len(epistles['roots']) < 1 and len(comments) < 1:
            no mail
        % endif
        <div id="new_message" style="display:none">
            <h3>Send a Message</h3>
            <form method="post" action="/messages/out" id="reply-form">
                <div id="message-subject">Subject: <input type="text" name="subject" /></div>
                Message: <textarea cols="30" rows="10" name="body"></textarea><br />
                To: <span id="new-message-to">-</span><br />
                <input type="hidden" name="recipient" id="recipient-hidden" /><br />
                <input type="hidden" name="parent_id" id="parent_id-hidden" /><br />
                <input type="submit" value="Send Message"></input>
            </form>
        </div>
