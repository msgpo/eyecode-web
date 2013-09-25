var sayings = {}
var saying_next = ["", ""]

function say_next() {
    var id_prev = saying_next[0];
    $("#" + id_prev).hide();

    saying_next = sayings[id_prev];
    var id_next = saying_next[0];
    var id_focus = saying_next[1];

    $("#" + id_next).show();

    if (id_focus != null) {
        $("#" + id_focus).focus();
    }
}

function say_first(id_next, id_focus) {
    saying_next = [id_next, id_focus];
    $("#" + id_next).show();
}

function link_sayings(id_prev, id_next, id_focus) {
    sayings[id_prev] = [id_next, id_focus];
}

function set_answer(id, value) {
    $("#" + id).val(value);
}

function validate_number(id) {
    var val = $("#" + id).val();

    if ((val == null) || (val.trim().length == 0) || isNaN(val)) {
        alert("I'm looking for a number");
        return false;
    }

    return true;
}


function nowUTC() {
    var now = new Date();
    return Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(),
        now.getHours(), now.getMinutes(), now.getSeconds(), now.getMilliseconds());
}
