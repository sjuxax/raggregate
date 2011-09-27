<form method="post" action="/vote/${pageargs['direction']}" style="display: none" id="${pageargs['direction']}-${pageargs['id']}">
    <input type="hidden" value="${pageargs['target']}" name="target_type" />
    <input type="hidden" value="${pageargs['id']}" name="sub_id" />
    ##@TODO: make jump_to only redirect to sites without our master domain instead of a full url
    ##this will need changes in views.py too
    % if 'jump_to' in pageargs:
        <input type="hidden" value="${pageargs['jump_to']}" name="jump_to" />
    % endif
</form>
