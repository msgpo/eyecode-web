<%page args="title" />

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <title>eyeCode - ${title}</title>
  <link rel="stylesheet" href="css/style.css" type="text/css" />
  <link rel="stylesheet" href="css/terminal-${colorscheme}.css" type="text/css" />
  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
  <script type="text/javascript" src="http://ajax.aspnetcdn.com/ajax/jquery.validate/1.10.0/jquery.validate.min.js"></script>
  <script type="text/javascript" src="scripts/discourse.js"></script>
</head>

<%def name="answers(questions, name)">
    % for (i, ans) in enumerate(questions[name]):
        <input class="answer" type="button" value="${ans}" onclick="set_answer('q-${name}', ${i}); say_next()" />
        <br />
    % endfor
</%def>

<%def name="question(questions, name, label)">
    <label for="${name}">${label}</label>
    <select class="question" id="q-${name}" name="${name}">
        % for (i, ans) in enumerate(questions[name]):
            <option value="${i}">${ans}</option>
        % endfor
    </select>
    <br />
</%def>

<%def name="trial_image_src(trial)">
    images/${trial.program_base}_${trial.program_version}.${trial.language_ext()}-${image_width}x${image_height}-${colorscheme}.png
</%def>

<%def name="progress(num, total)">
    <div style="font-size: 1.5em;">
        % for i in range(1, total + 1):
            % if i == num:
                <span class="special">&bull;</span>
            % else:
                &middot;
            % endif
        % endfor
    </div>
</%def>

<body>
<div id="header">
    <h1 style="margin: 0; padding: 0; display:inline-block;">eyeC&#9679;de</h1>
    <span style="font-size: 1.15em; font-weight: normal; margin-left: 5px; vertical-align: middle;">[hacking for science]</span>
</div>
<div id="main">
