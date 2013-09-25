<%include file="header.mako" args="title='Qualification results'" />
<div style="text-align: center;">
    <img src="images/term_${term}.png" />
</div>
<div class="dialog" style="display: block;">
    % if msg == "pass":
        <h2>Congratulations!</h2>
        <p>
            You passed the qualification test.
        </p>
    % elif msg == "fail":
        <h2>We're Sorry</h2>
        <p>
            You missed one or more questions on the qualification test.
        </p>
    % elif msg == "timeout":
        <h2>We're Sorry</h2>
        <p>
            You took too long to complete the qualification test.
        </p>
    % endif
</div>
<%include file="footer.mako" />
