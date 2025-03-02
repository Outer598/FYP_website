$(document).ready(function () {
    $("#login").click(function () {
        var email = $("#email").val();
        var password = $("#password").val();

        // Simple validation
        if (email === "" || password === "") {
            alert("Please fill in both email and password.");
            return;
        }

        $.ajax({
            url: "/login",  // Flask login route
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ email: email, password: password }),
            success: function (response) {
                console.log("Login response:", response);
                // Redirect based on user type
                if (response.redirect_url) {
                    $(".message").css("background", '#228B22');
                    $(".message h6").html(`Login successful. Redirecting...`);
                    $(".message").fadeIn(1000).fadeOut(1000);
                    setTimeout(function() {
                        window.location.href = response.redirect_url;
                    }, 2000);
                } else {
                    console.log("No redirect URL in response");
                    $(".message").css("background", '#FF3131');
                    $(".message h6").html(`Login successful but no redirect.`);
                    $(".message").fadeIn(1000).fadeOut(1000);
                }
            },
            error: function (xhr) {
                console.log("Login error:", xhr.responseJSON);
                $(".message").css("background", '#FF3131');
                $(".message h6").html(`Login Failed: ${xhr.responseJSON?.error || 'Unknown error'}`);
                $(".message").fadeIn(1000).fadeOut(1000);
            }
        });
    });

    // Global AJAX error handler for authorization errors
    $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
        if (jqXHR.status === 401 || jqXHR.status === 403) {
            // Get error message from response
            var errorMessage = "Access error";
            if (jqXHR.responseJSON && jqXHR.responseJSON.error) {
                errorMessage = jqXHR.responseJSON.error;
            }
            
            // Display error message
            $(".message").css("background", '#FF3131');
            $(".message h6").html(`${errorMessage}`);
            $(".message").fadeIn(1000).fadeOut(1000);
            
            // Optionally redirect after a delay
            if (jqXHR.status === 401) {
                setTimeout(function() {
                    window.location.href = "/";  // Redirect to login page
                }, 2000);
            }
        }
    });
});