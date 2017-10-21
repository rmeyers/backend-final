
$(document).ready(function() {
  // Add smooth scrolling to all links
  $("a").on('click', function(event) {

    // Make sure this.hash has a value before overriding default behavior
    if (this.hash !== "") {
      // Prevent default anchor click behavior
      event.preventDefault();

      // Store hash
      var hash = this.hash;

      // Using jQuery's animate() method to add smooth page scroll
      // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
      $('html, body').animate({
        scrollTop: $(hash).offset().top - 130
      }, 800, function(){

        // Add hash (#) to URL when done scrolling (default click behavior)
        window.location.hash = hash;
      });
    } // End if
  });

  function signInCallback(authResult) {
    if (authResult['code']) {

      // Hide the sign-in button now that the user is authorized
      $('#signinButton').attr('style', 'display: none');

      // Send the one-time-use code to the server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main restaurants page
      $.ajax({
        type: 'POST',
        url: '/gconnect?state={{STATE}}',
        processData: false,
        data: authResult['code'],
        contentType: 'application/octet-stream; charset=utf-8',
        success: function(result) {
          // Handle or verify the server response if necessary.
          if (result) {
            $('#result').html('Login Successful!</br>'+ result + '</br>Redirecting...')
           setTimeout(function() {
            window.location.href = "/dashboard/";
           }, 4000);


        } else if (authResult['error']) {

      console.log('There was an error: ' + authResult['error']);
    } else {
          $('#result').html('Failed to make a server-side call. Check your configuration and console.');
           }
        }
  }); }}
});


