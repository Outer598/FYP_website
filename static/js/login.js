$(document).ready(function () {
    $("#login").click(function () {
        var email = $("#email").val();
        var password = $("#password").val();

        if (email === "" || password === "") {
            $(".message").css("background", '#FF3131');
            $(".message h6").html(`Please provide both email and password`);
            $(".message").fadeIn(1000).fadeOut(1000);
            return;
        }

        $.ajax({
            url: "/login",  // Make sure this matches your actual endpoint
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ email: email, password: password }),
            xhrFields: {
                withCredentials: true  // Important: allow cookies to be sent with request
            },
            success: function (response) {
                console.log("Login response:", response);

                if (response.tokens) {
                    // Store tokens in localStorage for AJAX requests
                    localStorage.setItem('access_token', response.tokens.access_token);
                    localStorage.setItem('refresh_token', response.tokens.refresh_token);
                    localStorage.setItem('user_type', response.tokens.user_type);

                    // Show success message
                    $(".message").css("background", '#228B22');
                    $(".message h6").html(response.message);
                    $(".message").fadeIn(1000);

                    // Delay redirect to ensure token is saved
                    setTimeout(function () {
                        if (response.redirect_url) {
                            window.location.href = response.redirect_url;
                        } else {
                            console.log("No redirect URL in response");
                            $(".message").css("background", '#FF3131');
                            $(".message h6").html(`Login success, but no redirect URL received.`);
                            $(".message").fadeIn(1000).fadeOut(1000);
                        }
                    }, 1500);
                } else {
                    $(".message").css("background", '#FF3131');
                    $(".message h6").html(`Login failed: ` + response.message);
                    $(".message").fadeIn(1000).fadeOut(1000);
                }
            },
            error: function (xhr, status, error) {
                console.error("Login AJAX error:", status, error);
                let response = JSON.parse(xhr.responseText);
                console.log(response);
                $(".message").css("background", '#FF3131');
                $(".message h6").text(response.message);
                $(".message").fadeIn(1000).fadeOut(1000);
            }
        });
    });
});