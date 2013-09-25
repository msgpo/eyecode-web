<%include file="header.mako" args="title='Thank you'" />

<div style="text-align: center;">
    <h1>Thank you!</h1>

    % if experiment.is_mt():
        <h3>Confirmation Code: ${confirm_code}</h3>
    % endif

    <img src="images/term_bliss.jpg" style="border: 2px solid #333;" />
</div>
<%include file="footer.mako" />
