<%include file="header.mako" args="title='Programs'" />
<%namespace file="header.mako" import="trial_image_src" />

<% completed = len(filter(lambda t: t.ended, experiment.trials)) %>

% if completed < 5:
    <div style="float: left;">
        <img src="images/term_sick.png" />
    </div>
    <div style="float: left; margin-left: 15px; padding-top: 30px;">
        <div class="speech">
            Tell me what <span class="special">YOU</span> think the programs below will output.
            <br />
            Be quick, but try not to make mistakes!
        </div>
    </div>
% elif completed < 9:
    <div style="float: left;">
        <img src="images/term_half_sick.png" />
    </div>
    <div style="float: left; margin-left: 15px; padding-top: 50px;">
        <span class="speech">Almost there! Just a few more programs...</span>
    </div>
% else:
    <div style="float: left;">
        <img src="images/term_half_sick.png" />
    </div>
    <div style="float: left; margin-left: 15px; padding-top: 50px;">
        <span class="speech">One program left!</span>
    </div>
% endif
<br style="clear: both;" />

<ol class="programs" style="line-height: 2em;">
    % for trial in sorted(experiment.trials, key=lambda t: t.id):
        <li>

        % if trial.ended:
            [Done]&nbsp;
            <span class="done">
                ${words[trial.id % len(words)]}.${trial.language_ext()}
            </span>
        % else:
            [<a href="start_trial?id=${trial.id}&nonce=${experiment.name}" onclick="finished = true">Start</a>]
            <span class="notdone">
                ${words[trial.id % len(words)]}.${trial.language_ext()}
            </span>
        % endif

        </li>

        <!-- Pre-load image -->
        <img style="display: none;" src="${trial_image_src(trial)}" />
    % endfor
</ol>
<script type="text/javascript">
    var finished = false;

    window.onbeforeunload = function () {
        if (!finished) {
            finished = true;
            return "Are you sure? I really need to know what these programs do!"
        }
    }
</script>
<%include file="footer.mako" />
