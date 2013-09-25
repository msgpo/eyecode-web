<%include file="header.mako" args="title='Qualification test'" />
<%namespace file="header.mako" import="answers,question,progress" />

<% 
    import random
    lang_cap = language.capitalize()
    questions = {
        "var": ["int x = 7", "x = 7", "x <- 7", "x == 7"],
        "fun": ["f(x: int): int =<br />&nbsp;&nbsp;return x + 1", "def f(x):<br />return x + 1", "int f(int x) {<br />&nbsp;&nbsp;&nbsp;&nbsp;return x + 1;<br />}", "def f(x):<br />&nbsp;&nbsp;&nbsp;&nbspreturn x + 1"],
        "print": ["print \"hello\", \"hello\"", "System.out.println(\"hello\", \"hello\");", "print \"hello\"<br />print \"hello\"", "System.out.println(\"hello\");<br />System.out.println(\"hello\");"],
        "list": ["x = []<br />x.append(5)", "x = new list()<br />x.add(5)", "ArrayList x;<br />x.add(5);", "ArrayList x = new ArrayList();<br />x.add(5);"],
        "loop": ["for x in [1, 2, 3]:<br />&nbsp;&nbsp;&nbsp;&nbsp;print x",
                 "int[] list = new int[] { 1, 2, 3 };<br />for (int i = 0; i < list.length; i++)<br />&nbsp;&nbsp;&nbsp;&nbsp;System.out.println(x[i]);",
                 "foreach (x: int in [1, 2, 3])<br />&nbsp;&nbsp;&nbsp;&nbsp;print x",
                 "int[] list = new int[] { 1, 2, 3 };<br />list.each(x => System.out.println(x));"
                ]
    }
%>

<%def name="quals_answers(qname, submit=False)">
    <div style="text-align: left;">
        <ol>
            % for (i, ans) in enumerate(questions[qname]):
                <li style="margin-bottom: 2em;"><pre class="code">${ans}</pre>

                % if submit:
                    <input class="answer" type="button" value="Answer # ${i + 1}" onclick="set_answer('q-${qname}', '${i}'); $('#form-quals').submit();" />
                % else:
                    <input class="answer" type="button" value="Answer # ${i + 1}" onclick="set_answer('q-${qname}', '${i}'); say_next();" />
                % endif
                </li>
            % endfor
        </ol>
    </div>
</%def>

<div style="text-align: center;">
    <img src="images/brain_steam.png" />
</div>
<div id="hello" class="dialog">
    Hello! To make sure you're qualified for this experiment,
    <br />
    we need to ask you a few <span class="special">${lang_cap} questions</span>.
    <br />
    <br />
    You will only have <span class="name">10 minutes</span> to complete this test
    <br />
    and you must answer <span class="name">all questions correctly</span>.
    <br />
    <br />
    <input class="answer" type="button" value="Continue" onclick="$('#started').val(new Date()); say_next()" />
</div>
<div id="var" class="dialog">
    <h3>Question 1</h3>
    Which is the proper way to <span class="special">declare a variable</span> in ${lang_cap}?
    ${quals_answers("var")}
</div>
<div id="fun" class="dialog">
    <h3>Question 2</h3>
    Which is the proper way to <span class="special">declare a function</span> in ${lang_cap}?
    ${quals_answers("fun")}
</div>
<div id="print" class="dialog">
    <h3>Question 3</h3>
    Which the proper way to <span class="special">print "hello" on two separate lines</span> in ${lang_cap}?
    ${quals_answers("print")}
</div>
<div id="list" class="dialog">
    <h3>Question 4</h3>
    Which of the following is the proper way to <span class="special">add an item to a list</span> in ${lang_cap}?
    ${quals_answers("list")}
</div>

<div id="loop" class="dialog">
    <h3>Question 5</h3>
    Which of the following is the proper way to <span class="special">loop through a list</span> in ${lang_cap}?

    <form id="form-quals" action="qualification" method="POST" onsubmit="$('#ended').val(new Date())">
        <input id="started" type="hidden" name="started" value="" />
        <input id="ended" type="hidden" name="ended" value="" />
        <input type="hidden" name="workerId" value="${workerId}" />
        <input type="hidden" name="language" value="${language}" />
        <input id="q-var" type="hidden" name="var" value="" />
        <input id="q-fun" type="hidden" name="fun" value="" />
        <input id="q-print" type="hidden" name="print" value="" />
        <input id="q-list" type="hidden" name="list" value="" />
        <input id="q-loop" type="hidden" name="loop" value="" />

        ${quals_answers("loop", submit=True)}
    </form>
</div>

<script type="text/javascript">
    $(function() {
        link_sayings("hello", "var");
        link_sayings("var", "fun");
        link_sayings("fun", "print");
        link_sayings("print", "list");
        link_sayings("list", "loop");
        say_first("hello");
    });
</script>
<%include file="footer.mako" />
