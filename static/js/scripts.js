window.onload = function() {
    var form = document.querySelector('form');
    form.onsubmit = function(e) {
        var inputs = form.querySelectorAll('input[type=text], input[type=password], input[type=number]');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].value == '') {
                alert('All fields must be filled out');
                e.preventDefault();
                return;
            }
        }
    }
}
