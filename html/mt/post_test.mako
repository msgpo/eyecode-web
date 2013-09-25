<%include file="header.mako" args="title='Post test'" />
<%namespace file="header.mako" import="answers,question,progress" />
<%
    questions = {
        "difficulty": ["No, they were easy", "A little, but not too bad", "Yeah they were kinda hard"],
        "correct": ["Most or all of them", "Around half", "Only a few or none"]
    }
%>

<div style="text-align: center;">
    <img src="images/term_happy.png" />
</div>
<div id="thanks" class="dialog">
    Thank you so much! I'm feeling 100% better now.
    <br />
    <input class="answer" type="button" value="You're welcome!" onclick="say_next()" />
</div>
<div id="difficulty" class="dialog">
    ${progress(1, 3)}
    What did you think of those programs? Were they hard?
    <br />
    ${answers(questions, "difficulty")}
</div>
<div id="correct" class="dialog">
    ${progress(2, 3)}
    OK, good to know. And how many do you think you got right?
    <br />
    ${answers(questions, "correct")}
</div>
<div id="thoughts" class="dialog">
    ${progress(3, 3)}
    Great! Any final thoughts?
    <br />
    <textarea id="qq-thoughts" rows="5" cols="40" onchange="set_answer('q-thoughts', $(this).val())"></textarea>
    <br />
    <input class="answer" type="button" value="Next" onclick="say_next()" />
</div>
<div id="confirm" class="dialog">
    Here's what I heard you say. Does this sound right?
    <br />
    <form action="post_test" method="POST">
        <input type="hidden" name="id" value="${experiment.id}" />
        <input type="hidden" name="nonce" value="${experiment.name}" />

        ${question(questions, "difficulty", "Were the programs hard?")}
        ${question(questions, "correct", "How many did you get right?")}

        <br />
        <label for="thoughts">Final thoughts:</label>
        <br />
        <textarea id="q-thoughts" name="thoughts" rows="5" cols="50"></textarea>

        <br />
        <input class="answer" type="submit" value="Done" />
    </form>
</div>


<!-- Pre-load final image -->
<img src="images/term_bliss.jpg" style="display: none;" />

<script type="text/javascript">
    $(function() {
        link_sayings("thanks", "difficulty");
        link_sayings("difficulty", "correct");
        link_sayings("correct", "thoughts", "qq-thoughts")
        link_sayings("thoughts", "confirm")
        say_first("thanks");
    });
</script>
<%include file="footer.mako" />
