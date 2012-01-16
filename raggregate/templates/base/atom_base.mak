% if 'atom.enabled' not in request.registry.settings or request.registry.settings['atom.enabled'] != 'true':
	<% return %>
% endif
<?xml version="1.0" encoding="utf-8"?>

<feed xmlns="http://www.w3.org/2005/Atom">

    <%block name="feed_metadata">
        <title>default</title>
        <subtitle>default</subtitle>
        <link href="${request.url}" rel="self" />
        <id>default+default+${request.registry.settings['site.site_name']}</id>
    </%block>
    <link href="${request.route_url('home')}" />
    <updated>${last_update}</updated>

    ${self.body()}

</feed>
