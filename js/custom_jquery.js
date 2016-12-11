// This document contains all custom jQuery functions
$(document).ready(function() {
    $('#loginForm').validate({
        rules: {
            email: {
                //required: true,
                email: true
            }
        },
        messages: {
            email: {
                required: "Please enter an email address",
                email: "Please enter a valid email address"
            }
        }
    })
});
