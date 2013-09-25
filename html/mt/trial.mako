<%include file="header.mako" args="title='Trial'" />
<%namespace file="header.mako" import="trial_image_src" />

<div style="margin-left: ${image_offset}px; min-width: ${image_width + 350}px;">
    <div style="float: left; width: ${image_width + 5}px;">
        <img id="program" src="${trial_image_src(trial)}" />
    </div>
    <div style="float: left; width: 300px;">
        <h3>What will this program output?</h3>

        <form action="end_trial" method="post" onsubmit="return validateResponse();">
            <input type="hidden" name="id" value="${trial.id}" />
            <input type="hidden" name="nonce" value="${nonce}" />
            <input id="image_x" type="hidden" name="image_x" value="0" />
            <input id="image_y" type="hidden" name="image_y" value="0" />
            <input id="responses_js" type="hidden" name="responses_js" value="[]" />

            <textarea id="response" name="response" cols="35" rows="15"></textarea>
            <br />
            <br />
            <input id="submit1" type="submit" value="Continue" />
        </form>
    </div>
    <br style="clear: both;" />
</div>

<script type="text/javascript">
    var finished = false;
    var responses = []

    function validateResponse() {
        resp_val = $("#response").val();

        if ((resp_val == null) || (resp_val.length < 1)) {
            alert("Please enter what you think the program will output");
            return false;
        }

        finished = true;
        $("#responses_js").val(JSON.stringify(responses))
        $("#submit1").attr("disabled", "disabled");
        return true;
    }

    $(function() {
        $("#image_x").val($("#program").offset().left);
        $("#image_y").val($("#program").offset().top);

        $("#response").focus();
        $("#response").keypress(function(event) {
            var now = nowUTC();
            var c = String.fromCharCode(event.which);

            if (!event.shiftKey) {
                c = c.toLowerCase();
            }

            var resp_val = $("#response").val() + c;
            responses.push([now, resp_val]);
        });
    })

    window.onbeforeunload = function () {
        if (!finished) {
            return "Are you sure? I really need to know what this program does!"
        }
    }

</script>

<%include file="footer.mako" />
