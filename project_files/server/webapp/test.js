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
		messages = 0;
		connect();
		function connect(){	
			try{ //this should be in a try-catch block so we can log errors
				// Note I changed both ports to 6354 for consistency -- works better for testing this way
				var EC2 	= new WebSocket("ws://ec2-174-129-190-18.compute-1.amazonaws.com:6354/websocket");
				//var laptop  = new WebSocket("ws://localhost:6354/websocket");
				var laptop  = new WebSocket("ws://localhost:6354/websocket"); 
				
				//Make sure you set the binaryType of the websockets to arraybuffer, so that they are handling raw bytes.
				EC2.binaryType = "arraybuffer";
				laptop.binaryType = "arraybuffer";
				
				
				console.log("EC2:");
				console.log(EC2);
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
					message("Received message '" + msg.data + "' from the EC2 server. Forwarding to the laptop.");
					laptop.send(msg.data);
				}
	
				/* symmetrically */
				laptop.onmessage = function(msg){
					message("Received message '" + msg.data + "' from the laptop. Forwarding to the EC2 server.");
					EC2.send(msg.data);
				}
	
				/* That's it! Now just provide a way of closing them */
				$('#disconnect').click(function(){
					EC2.close();
					laptop.close();
				});
	
				$('#send').click(function(){	
					var toRemote = $('#toRemote').val();
					var toLocal  = $('#toLaptop').val();
					
					if(toLocal){
						message("Sending to laptop: " + toLocal);
						laptop.send(toLocal);
					}			
					if(toRemote){
						message("Sending to remote: " + toRemote);
						EC2.send(toRemote);
					}
				});
			}
			catch(exception){
				message('<p>Error: '+exception); 			
			}
		}
		
		/* simply for informing the user of an event */
		function message(msg){
			messages++;
			console.log(messages+" messages");
			var chatdiv = document.getElementById('chatbox');
			chatbox = $('#chatbox');
			var newMessage = document.createElement("div");
			newMessage.className+="message";
			newMessage.innerHTML = "<p class = 'messageP'>"+msg+"</.p>";
			chatdiv.appendChild(newMessage);
			if(messages > 5){
				chatdiv.removeChild(chatdiv.firstChild);
			}		
		};
			
	}
});
