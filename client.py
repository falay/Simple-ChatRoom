import sys, os, tkinter
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

BUFSIZE = 1024

def error_check(condition, mesg):

	if not condition:
		print('Error:', mesg)
		sys.exit(0)

def encode_mesg(mesg):

	return bytes( mesg, 'utf-8' )

def decode_mesg(mesg):

	return mesg.decode('utf-8').strip()


class Daemon(Thread):

	def __init__(self, handler):
		super(Daemon, self).__init__(target=handler)
		self.daemon = True



class Connector:

	def __init__(self, host, port):

		try:
			self.client = socket( AF_INET, SOCK_STREAM )
			self.client.connect( (host, port) )
		except Exception as e:
			error_check( False, str(e) )

		self.receive_message_thread = Daemon( self.receive )
		self.receive_message_thread.start()
		self.show_connected_users_thread = Daemon(self.show_users)
		self.show_connected_users_thread.start()


	def set_message_box(self, message_box):

		self.message_box = message_box

	def receive(self):

		while True:
			try:
				mesg = decode_mesg( self.client.recv(BUFSIZE) )
				#if not mesg.startswith('#'):
				self.message_box.insert( tkinter.END, mesg )
			except Exception:
				pass


	def show_users(self):

		'''
		mesg = decode_mesg( self.client.recv(BUFSIZE) )
		if mesg.startswith('#'):
			print('Users:', mesg)
		'''
		pass

	def send(self, message):
		
		self.client.send( encode_mesg(message) )








class GUI_Manager:

	def __init__(self, connector):

		self.connector = connector
		self.login_creator()
			

	def login_creator(self):

		self.login_window = tkinter.Tk()
		self.login_window.title( 'RobotGo Chat Room Login' )
		
		# Label
		tkinter.Label( self.login_window, text='Username:' ).grid( row=1, column=1 )
		# Entry
		username_text  = tkinter.Entry( self.login_window )
		username_text.grid( row=1, column=2 )
		tkinter.Button( self.login_window, text='login', command=lambda:self.login(username_text.get()) ).grid( row=4, column=2 )		
		
		self.login_window.protocol( "WM_DELETE_WINDOW", lambda window=self.login_window:self.on_closing(window) )
		self.login_window.mainloop()

		


	def login(self, username):
		
		self.login_window.destroy()

		# Send username to the server
		self.connector.send( username )
		self.chatroom_window_creator( username )
		

	def chatroom_window_creator(self, username):

		self.chatroom_window = tkinter.Tk()
		self.chatroom_window.title( username+'\'s RobotGo Chat Room')

		message_frame = tkinter.Frame( self.chatroom_window )
		self.message_to_be_sent = tkinter.StringVar()
		self.message_to_be_sent.set('Type something to chat!')
		scrollbar = tkinter.Scrollbar( message_frame )
		message_box = tkinter.Listbox( message_frame, height=15, width=50, yscrollcommand=scrollbar.set )
		scrollbar.pack(side=tkinter.RIGHT)
		message_box.pack(side=tkinter.LEFT)
		self.connector.set_message_box( message_box )
		message_frame.pack()

		self.entry = tkinter.Entry( self.chatroom_window, textvariable=self.message_to_be_sent )
		self.entry.pack()
		tkinter.Button( self.chatroom_window, text='Send', command=self.click_button).pack()

	#	self.showing_online_users()

		self.chatroom_window.protocol( "WM_DELETE_WINDOW", lambda window=self.chatroom_window:self.on_closing(window) )
		self.chatroom_window.mainloop()

	#def showing_online_users(self):



	def click_button(self):

		self.connector.send( self.message_to_be_sent.get() )
		self.entry.delete( 0, 'end' )

	def on_closing(self, window):

		from tkinter import messagebox
		if messagebox.askokcancel("Exit", "Are you sure to exit the chatroom?"):
			if window == self.login_window:
				self.connector.send('dummy_name')

			self.connector.send('exit')
			self.connector.client.close()
			window.destroy()



class ChatRoomClient:

	def __init__(self, host, port):

		self.connector = Connector( host, port )
		self.GUI = GUI_Manager( self.connector )





if __name__ == '__main__':

	error_check( len(sys.argv) == 3, 'Usage: python client.py [host] [port]' )

	client = ChatRoomClient( sys.argv[1], int(sys.argv[2]) )

