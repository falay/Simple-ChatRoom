from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys, os



BUFSIZE = 1024
QUEUE_LEN = 5

def error_check(condition, mesg):

	if not condition:
		print('Error:', mesg)
		sys.exit(0)

def encode_mesg(mesg):

	return bytes( mesg, 'utf-8' )

def decode_mesg(mesg):

	return mesg.decode('utf-8').strip()


class ChatRoomServer:

	def __init__(self, host, port):

		self.master_thread = Thread(target=self.acceptor)
		self.clients_map = {}

		try:
			self.Server = socket( AF_INET, SOCK_STREAM )
			self.Server.bind( (host, port) )
		except Exception as e:
			error_check( False, str(e) )


	def run(self):

		self.Server.listen( QUEUE_LEN )
		self.master_thread.start()
		self.master_thread.join()
		self.Server.close()


	def acceptor(self):

		while True:
			try:
				client_socket, client_address = self.Server.accept()
				print( '[ChatRoom Server] client from %s:%s has connected to the server.' % client_address )
				Thread(target=self.client_handler, args=(client_socket,)).start()
			except Exception as e:
				error_check( False, str(e) )


	def client_handler(self, client_socket):

		client_name = decode_mesg( client_socket.recv( BUFSIZE ) )
		self.broadcast( '[System]************%s is now online.************' % client_name )

		self.clients_map[ client_name ] = client_socket

		# test for sending users information to this client
		print('Users:', self.clients_map)
		#client_socket.send( encode_mesg('#Users:'+str(self.clients_map)) )

		while True:
			try:

				message = decode_mesg( client_socket.recv( BUFSIZE ) ) 
				
				if self.check_client_not_exists( message, client_name ):
					break

				self.broadcast( client_name + ':' + message )
			
			except Exception as e:
				error_check( False, str(e) )


	def check_client_not_exists(self, message, client_name):

		client_socket = self.clients_map[ client_name ]
		# The client has exited
		if message == 'exit':
			self.broadcast( '[System]************%s is offline.************' % client_name )
			client_socket.close()
			del self.clients_map[ client_name ]
			return True

		return False
				

	def broadcast(self, message):

		for client_name, client_socket in self.clients_map.items():
			client_socket.send( encode_mesg(message) )


if __name__ == '__main__':

	error_check( len(sys.argv) == 3, 'Usage: python server.py [host] [port]' )

	server = ChatRoomServer( sys.argv[1], int(sys.argv[2]) )
	server.run()
