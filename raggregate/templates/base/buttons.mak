<%inherit file="base.mak"/>
<h2>Share Buttons on ${request.registry.settings['site.site_name']}</h2>
<p>You can place these buttons your web site to make it easier for users to share their posts.</p>
<img src="${static_base}images/button1.png" /><br />
Code to install this button:
<div style="margin-left: 20px; background-color: #f6f6f6">
    &lt;a href=&quot;javascript:void(0)&quot; onclick=&quot;window.location = &apos;${request.route_url('post', _query=[('new_post', 'y')])}&amp;url=&apos; + encodeURIComponent(window.location) + &apos;&amp;title=&apos; + encodeURIComponent(window.document.title) + &apos;&amp;from=button&apos;&quot;&gt; &lt;img src=&quot;${static_base}images/button1.png&quot; /&gt; &lt;/a&gt;
</div>

