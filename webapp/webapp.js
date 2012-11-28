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
			var EC2 	= new WebSocket("ws://[your-amazon-IP-address].amazonaws.com:8080/websocket/");
			var laptop  = new WebSocket("ws://169.254.134.89:6354/websocket");
			

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
		}
		
		/* simply for informing the user of an event */
		function message(msg){
			$(msg + "\n").appendTo('#chatbox');
		};
			
	}
});