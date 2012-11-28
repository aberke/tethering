/* 
Author: Neil Fulwiler, Alex Berke
Date  : 11.26.2012
Usage : this will be the web app that we will use on our
		smart phones. But how?? I don't know. Borrowed 
		substantially from http://net.tutsplus.com/tutorials/javascript-ajax/start-using-html5-websockets-today/
*/

$(document).ready(function(){
	if(!("WebSocket" in window)){
		$('<p>Browswer does not suppoer websockets.</p>').appendTo('#container');
	}
	else{
		connect();
		function connect(){	
			var EC2 	= new WebSocket("ws://ec2-174-129-190-18.compute-1.amazonaws.com:8080/websocket");
			var laptop  = new WebSocket("ws://localhost:6354/websocket");
	
			//message('EC2 Status: '+EC2.readyState); 
			//message('laptop Status: '+laptop.readyState);

			/* inform the user of the actions of the remote websocket */
			EC2.onopen = function(){
				message("EC2 websocket opened");
			};
			EC2.onclose = function(){
				message("EC2 websocket closed");
			};

			/* inform the user of the actions of the local websocket */
			laptop.onopen = function(){
				message("laptop websocket opened");
			};
			laptop.onclose = function(){
				message("laptop websocket closed");
			};


			/* Now when we receive a message from either of them,
			   we simply send it to the other */
			EC2.onmessage = function(msg){
				message("Received message '" + msg + "' from the EC2 server. Forwarding to the laptop.");
				laptop.send(msg);
			}

			/* symmetrically */
			laptop.onmessage = function(msg){
				message("Received message '" + msg + "' from the laptop. Forwarding to the EC2 server.");
				EC2.send(msg);
			}

			/* That's it! Now just provide a way of closing them */
			$('#disconnect').click(function(){
				EC2.close();
				laptop.close();
			});

			$('#send').click(function(){	
				var toRemote = $('#toRemote').val();
				var toLocal  = $('#toLaptop').val();
		
				if(toRemote){
					message("Sending to remote: " + toRemote);
					EC2.send(toRemote);
				}
				
				if(toLocal){
					message("Sending to laptop: " + toLocal);
					laptop.send(toLocal);
				}
			});

		}
		
		/* simply for informing the user of an event */
		function message(msg){
			//alert("Message: " + msg);
			$('#chatbox').append("<p class='message'>"+msg+"</p>");
		};
			
	}
});
