$(function(){
	$('#login').click(function(){
		var user = $('#empId').val();
        var password = $('#password').val();

		$.ajax({
            //Uses testapp.py to check if login credentials are satisfied
			url: '/loginCheck',
			data: $('form').serialize(),
            type: 'POST',

			success: function(response){
                obj = JSON.parse(response);

                //If login credentials are satisfied, login and redirect to viz page
                if(obj.status == "OK"){
                    document.getElementById("empId").value = "";
                    document.getElementById("password").value = "";
                    var confMessage = "Logging in, " + user + "!";
                    document.getElementById("confirm").innerHTML = confMessage;
                    document.getElementById("confirm").style.textAlign = "center";
                    window.location.href = "/main-page";

                }
                //If login credentials are not satisfied, prompt user to login again
                else{
                    var errorMessage = obj.user;
                    //Reset both employee ID and password if employee ID is incorrect
                    if(errorMessage == "Employee ID must contain 5 digits." || errorMessage == "Incorrect employee ID."){
                        document.getElementById("empId").value = "";
                        document.getElementById("password").value = "";
                    } else {
                        //Reset just password if employee ID is found in DB but incorrect password
                        document.getElementById("password").value = "";
                    }

                    document.getElementById("confirm").innerHTML = errorMessage;
                    document.getElementById("confirm").style.textAlign = "center";
                }
			},
			error: function(error){
				console.log(error);
			}
        });

	});
});

function toggler(e){
    //Toggle FA icon for seeing/hiding password
    if( e.className == "fa fa-eye-slash" ) {
        e.classList.remove("fa-eye-slash")
        e.className += " fa fa-eye"
        document.getElementById('password').type="text";
    } else {
        e.classList.remove("fa-eye")
        e.className += " fa-eye-slash"
        document.getElementById('password').type="password";
    }
}
