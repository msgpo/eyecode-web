<%include file="header.mako" args="title='Pre test'" />
<%namespace file="header.mako" import="answers,question,progress" />
<%
    questions = {
        "gender": ["I'm a girl", "I'm a guy", "I'd rather not say"],
        language: ["< 1 year", "1-2 years", "2-5 years", "5-10 years", "> 10 years"],
        "education": ["I don't have a degree", "Bachelors", "Masters", "Ph.D.", "Something else"],
        "major": ["I am now", "I did in the past", "Nope"],
        "programming": ["< 1 year", "1-2 years", "2-5 years", "5-10 years", "> 10 years"],
    }

    is_mt = len(hitId) > 0
%>

<div style="text-align: center;">
    <img src="images/term_sick.png" />
</div>
<div id="hello" class="dialog">
    Oh, hello there! My name is <span class="name">Tim</span>.
    <br />
    I got a virus, and I'm feeling a little under the weather.
    <br />
    I really need to run some <span class="special">${language.capitalize()} programs</span>, but my head is all <em>fuzzy</em>.
    <br />
    <br />
    Would you be willing to help?
    <br />
    <input class="answer" type="button" value="Of course!" onclick="say_next()" />
</div>

% if is_mt:
    <div id="consent" class="consent">
        <p>IRB Study #0804000155 (97-763)</p>
        <h1>INDIANA UNIVERSITY INFORMED CONSENT FOR</h1>
        <h2>Concepts and Percepts</h2>
        <p>You are invited to participate in a research study of how what we have learned can influence how people think, act, and make decisions.  You were selected as a possible subject because you contacted our research team expressing interest in participating.  We ask that you read this form and ask any questions you may have before agreeing to be in the study.</p>
        <p>The study is being conducted by Dr. Robert Goldstone in the Department of Psychological and Brain Sciences.</p>
        <h3>STUDY PURPOSE</h3>
        <p>The purpose of this study is to better understand the ways that people see objects can change as they learn new tasks.</p>
        <h3>NUMBER OF PEOPLE TAKING PART IN THE STUDY:</h3>
        <p>If you agree to participate, you will be one of approximately 15000 subjects who will be participating in this research.</p>
        <h3>PROCEDURES FOR THE STUDY:</h3>
        <p>If you agree to be in the study, you will be presented with several straightforward tasks to complete.  These tasks will include responding with key strokes to images displayed on a computer monitor and may involve learning what categories objects belong in, determining if objects are identical or related, and transferring what you learn about objects in one training task to a related task.</p>
        <p>The entire session should take a maximum of 60 minutes. You may only participate in the experiment once.</p>
        <h3>RISKS OF TAKING PART IN THE STUDY:</h3>
        <p>Participation in this study involves a potential risk of loss of confidentiality. </p>
        <h3>BENEFITS OF TAKING PART IN THE STUDY:</h3>
        <p>An understanding of how people change the way they see the world as they learn can help us to find more efficient methods to teach information and develop technologies that increase the speed of learning. You benefit from this experience because you learn something about how an experiment is designed and conducted, what issues are of interest to cognitive scientists, and what kinds of group behaviors emerge when individuals try to reach their goals in an environment that consists largely of other individuals.</p>
        <h3>ALTERNATIVES TO TAKING PART IN THE STUDY:</h3>
        <p>An alternative to participating in the study is to choose not to participate.</p>
        <h3>CONFIDENTIALITY</h3>
        <p>Efforts will be made to keep your personal information confidential.  We cannot guarantee absolute confidentiality.  Your personal information may be disclosed if required by law. Your identity will be held in confidence in reports in which the study may be published and in databases in which results may be stored.  Organizations that may inspect and/or copy your research records for quality assurance and data analysis include groups such as the study investigator and his/her research associates, the IUB Institutional Review Board or its designees, and (as allowed by law) state or federal agencies, specifically the Office for Human Research Protections (OHRP), etc. who may want to access your research records. </p>
        <h3>PAYMENT</h3>
        <p>For participating in this study, you will receive a small payment of $1.00.</p>
        <h3>CONTACTS FOR QUESTIONS OR PROBLEMS</h3>
        <p>For questions about the study, contact the researcher Dr. Robert Goldstone at (812) 855-4853.  </p>
        <p>For questions about your rights as a research participant or to discuss problems, complaints or concerns about a research study, or to obtain information, or offer input, contact the IU Human Subjects Office at (812) 856-4242 or by email at irb@iu.edu </p>
        <h3>VOLUNTARY NATURE OF STUDY</h3>
        <p>Taking part in this study is voluntary.  You may choose not to take part or may leave the study at any time.  Leaving the study will not result in any penalty or loss of benefits to which you are entitled and you will be compensated for your time up to that point.  Your decision whether or not to participate in this study will not affect your current or future relations with the investigator(s).</p>
        <h3>SUBJECT'S CONSENT</h3>
        <p>By checking below, you acknowledge that you have read and understand the above information, the you are 18 years of age or older, and give your consent to participate in our internet-based study.</p>
        <p style="border: 1px solid red; padding: 5px;">
            <input type="checkbox" id="consent_checkbox" />I agree to take part in this study.
        </p>
        <p>Print this page if you want a copy for your records.</p>
        <p>Form date: April 3, 2012</p>
        <p>
            <img src="images/consent_irb.png" width="200px" />
        </p>
        <input id="consent_button" class="answer" type="button" value="Continue" disabled="disabled" onclick="say_next()" />
    </div>
% endif

<div id="gender" class="dialog">
    ${progress(1, 6)}
    Great! If you don't mind me asking, are you a girl or a guy?
    <br />
    ${answers(questions, "gender")}
</div>
<div id="age" class="dialog">
    ${progress(2, 6)}
    Okay. And how old are you?
    <br />
    <br />
    <div class="response">
        I'm <input id="qq-age" class="dialog-text age" type="text" onchange="set_answer('q-age', $(this).val())" /> years old
    </div>
    <br />
    <input class="answer" type="button" value="Next" onclick="say_next()" />
</div>
<div id="language" class="dialog">
    ${progress(3, 6)}
    Excellent! So how many years of <span class="special">${language.capitalize()}</span> programming experience do you have?
    <br />
    <br />
    <div class="response">
        <input id="qq-language_years" class="dialog-text age" type="text" onchange="set_answer('q-language_years', $(this).val())" /> years
    </div>
    <br />
    <input class="answer" type="button" value="Next" onclick="say_next()" />
</div>
<div id="education" class="dialog">
    ${progress(4, 6)}
    You sound smart! What's the highest degree that you've <span class="special">received</span>?
    <br />
    ${answers(questions, "education")}
</div>
<div id="major" class="dialog">
    ${progress(5, 6)}
    Are you majoring in <span class="special">Computer Science</span> now, or have you ever?
    <br />
    ${answers(questions, "major")}
</div>
<div id="programming" class="dialog">
    ${progress(6, 6)}
    Wow! Last question: how many years of <span class="special">programming experience</span> do you have overall?
    <br />
    <br />
    <div class="response">
        <input id="qq-programming_years" class="dialog-text age" type="text" onchange="set_answer('q-programming_years', $(this).val())" /> years
    </div>
    <br />
    <input class="answer" type="button" value="Next" onclick="say_next()" />
</div>
<div id="confirm" class="dialog">
    Here's what I heard you say. Does this sound right?
    <br />
    <form id="form-pre" action="pre_test" method="POST">
        <input type="hidden" name="hitId" value="${hitId}" />
        <input type="hidden" name="assignmentId" value="${assignmentId}" />
        <input type="hidden" name="workerId" value="${workerId}" />
        <input type="hidden" name="submitTo" value="${submitTo}" />
        <input type="hidden" name="language" value="${language}" />

        ${question(questions, "gender", "Your gender:")}

        <div class="response">
            You're <input id="q-age" name="age" class="dialog-text age" type="text" /> years old
        </div>

        <div class="response">
            Years of ${language.capitalize()} experience: <input id="q-language_years" name="${language}_years" class="dialog-text age" type="text" />
        </div>

        ${question(questions, "education", "Your highest degree:")}
        ${question(questions, "major", "Majoring in Computer Science:")}

        <div class="response">
            Years of programming experience: <input id="q-programming_years" name="programming_years" class="dialog-text age" type="text" />
        </div>

        <br />
        <input class="answer" type="submit" value="Start the experiment" />
    </form>
</div>

<script type="text/javascript">
    $(function() {
        $("#form-pre").validate({
            rules: {
                age: {
                    required: true,
                    minlength: 2,
                    digits: true
                },
                ${language}_years: {
                    required: true,
                    number: true
                },
                programming_years: {
                    required: true,
                    number: true
                }
            },

            messages: {
                age: "*",
                programming_years: "*",
                ${language}_years: "*"
            }
        });

        % if is_mt:
            $("#consent_checkbox").change(function() {
                if (this.checked) {
                    $("#consent_button").removeAttr("disabled");
                }
                else {
                    $("#consent_button").attr("disabled", "disabled");
                }
            });

            link_sayings("hello", "consent");
            link_sayings("consent", "gender");
        % else:
            link_sayings("hello", "gender");
        % endif

        link_sayings("gender", "age", "qq-age");
        link_sayings("age", "language", "qq-language_years");
        link_sayings("language", "education");
        link_sayings("education", "major");
        link_sayings("major", "programming", "qq-programming_years");
        link_sayings("programming", "confirm");
        say_first("hello");
    });
</script>
<%include file="footer.mako" />
