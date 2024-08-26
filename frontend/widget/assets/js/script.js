
$(document).ready(function() {

    // Credentials
    
    //---------------------------------- Add dynamic html bot content(Widget style) ----------------------------
    // You can also add the html content in html page and still it will work!
    var mybot = '<div class="chatCont" id="chatCont">'+
                                '<div class="bot_profile">'+
                                    '<img src="assets/img/bot2.svg" class="bot_p_img">'+
                                    '<div class="close">'+
                                        '<i class="fa fa-times" aria-hidden="true"></i>'+
                                    '</div>'+
                                '</div><!--bot_profile end-->'+
                                '<div id="result_div" class="resultDiv"></div>'+
                                '<div class="chatForm" id="chat-div">'+
                                    '<div class="spinner">'+
                                        '<div class="bounce1"></div>'+
                                        '<div class="bounce2"></div>'+
                                        '<div class="bounce3"></div>'+
                                    '</div>'+
                                    '<input type="text" id="chat-input" autocomplete="off" placeholder="Try typing here"'+ 'class="form-control bot-txt"/>'+
                                '</div>'+
                            '</div><!--chatCont end-->'+

                            '<div class="profile_div">'+
                                '<div class="row">'+
                                    '<div class="col-hgt">'+
                                        '<img src="assets/img/bot2.svg" class="img-circle img-profile">'+
                                    '</div><!--col-hgt end-->'+
                                    '<div class="col-hgt">'+
                                        '<div class="chat-txt">'+
                                            'Chat with us now!'+
                                        '</div>'+
                                    '</div><!--col-hgt end-->'+
                                '</div><!--row end-->'+
                            '</div><!--profile_div end-->';

    $("mybot").html(mybot);

    // ------------------------------------------ Toggle chatbot -----------------------------------------------
    $('.profile_div').click(function() {
        $('.profile_div').toggle();
        $('.chatCont').toggle();
        $('.bot_profile').toggle();
        $('.chatForm').toggle();
        document.getElementById('chat-input').focus();
    });

    $('.close').click(function() {
        $('.profile_div').toggle();
        $('.chatCont').toggle();
        $('.bot_profile').toggle();
        $('.chatForm').toggle();
    });

    function send(text) {
        const apiUrl = "http://localhost:8000/chat";
        
        // Prepare the payload with the user's input
        const payload = {
            content: text
        };
    
        // Send a POST request to the backend API
        fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            // Check if the response status is 200 (OK)
            if (response.ok) {
                return response.json(); // Parse the JSON response
            } else {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
        })
        .then(data => {
            // Extract the assistant's response from the API response
            const assistantResponse = data.response;
            
            // Display the assistant's response in the chat message container
            displayMessage("assistant", assistantResponse);

            // Log the assistant's response to the console
            console.log(assistantResponse);
        })
        .catch(error => {
            console.error(error.message);
            alert(error.message);
        });
    }

    // Function to display a message in the chat message container
    function displayMessage(role, messageContent) {
        // Example: Update the UI with the new message
        const chatContainer = document.getElementById("result_div");
        const messageElement = document.createElement("div");
        messageElement.className = role;
        messageElement.textContent = messageContent;
        chatContainer.appendChild(messageElement);
    }

	$('#chat-input').on('keypress', function(e) {
		if (e.which == 13) { // Enter key pressed
			let message = $(this).val();
			if (message.trim() !== '') {
				send(message);
				displayMessage("user", message); // Display user's message
				$(this).val(''); // Clear the input field
			}
			e.preventDefault(); // Prevent default Enter key behavior
		}
	});

    //---------------------------------------- Ascii Spinner ---------------------------------------------------
    function showSpinner() {
        $('.spinner').show();
    }
    function hideSpinner() {
        $('.spinner').hide();
    }

});
