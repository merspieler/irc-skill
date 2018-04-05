from threading import Thread
from time import sleep
from time import time
import select
import socket
import socks
import ssl
import re

from adapt.intent import IntentBuilder
from mycroft.audio import wait_while_speaking
from mycroft import MycroftSkill, intent_handler
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.util import normalize

#########################################
# RFC					#
# https://tools.ietf.org/html/rfc1459	#
# We don't fullfil all aspects of the	#
# RFC to keep it simple. If you think	#
# a command is needed, feel free to	#
# open a PR with your changes.		#
#########################################

LOGGER = getLogger(__name__)

class IRCSkill(MycroftSkill):
	def __init__(self):
		super(IRCSkill, self).__init__()
		# TODO make them configureable
		# TODO make them into lists
		# options
		self.settings['proxy'] = ""
		self.settings['proxy-port'] = 9050
		self.settings['proxy-user'] = ""
		self.settings['proxy-passwd'] = ""
		self.settings['server'] = "irc.freenode.net"
		self.settings['server-password'] = ""
		self.settings['port'] = 6697
		self.settings['channel'] = "mycroft"
		self.settings['channel-password'] = ""
		self.settings['user'] = "dummy|m"
		self.settings['password'] = ""
		self.settings['ssl'] = True
		self.settings['debug'] = False
		self.settings['msg-join'] = True
		self.settings['msg-part'] = True
		self.settings['msg-disc'] = True

		# IPC for comunicating between threads
		self.irc_lock = False
		self.irc_cmd = ""
		self.irc_str = ""

	def initialize(self):
		if self.settings['proxy'] != "":
			if self.settings['debug']:
				self.speak("Using proxy: " + self.settings['proxy'])
				self.speak("Port: " + str(self.settings['proxy-port']))
			socks.set_default_proxy(socks.SOCKS5, self.settings['proxy'], self.settings['proxy-port'], True, 'user','passwd')
			socket.socket = socks.socksocket

		self._irc_start_thread()

	@intent_handler(IntentBuilder('ConnectIntent').require('connect'))
	def handle_connect_intent(self, message):
		# TODO ability to connect to different server
		if self.con_thread.isAlive() == False:
			self._irc_start_thread()
		if self.irc_lock == False:
			self.speak("Connecting")
			self.irc_lock == True
			self.irc_cmd = "connect"
			self.irc_str = ""
			self.irc_lock = False

	@intent_handler(IntentBuilder('JoinIntent').require('join'))
	def handle_join_intent(self, message):
		# TODO ability to join to different channels
		if self.con_thread.isAlive() == False:
			self._irc_start_thread()
		if self.irc_lock == False:
			self.speak("Joining")
			self.irc_lock == True
			self.irc_cmd = "join"
			self.irc_str = ""
			self.irc_lock = False

	@intent_handler(IntentBuilder('PartIntent').require('part'))
	def handle_part_intent(self, message):
		# TODO ability to join to different channels
		if self.con_thread.isAlive() == False:
			self._irc_start_thread()
		if self.irc_lock == False:
			self.speak("Parting")
			self.irc_lock == True
			self.irc_cmd = "part"
			self.irc_str = ""
			self.irc_lock = False

	@intent_handler(IntentBuilder('DisconnectIntent').require('disconnect'))
	def handle_disconnect_intent(self, message):
		# TODO ability to disconnect from different server
		if self.con_thread.isAlive() == False:
			self._irc_start_thread()
		if self.irc_lock == False:
			self.speak("Disconnecting")
			self.irc_lock == True
			self.irc_cmd = "disconnect"
			self.irc_str = ""
			self.irc_lock = False

	@intent_handler(IntentBuilder('SendIntent').require('send'))
	def handle_send_intent(self, message):
		# TODO ability to send to different users and channels
		if self.con_thread.isAlive() == False:
			self._irc_start_thread()
		if self.irc_lock == False:
			response = self.get_response("get_msg")
			if response != None:
				self.irc_lock == True
				self.irc_cmd = "send"
				self.irc_str = response
				self.irc_lock = False
			else:
				self.speak("I didn't understand a message")

	@intent_handler(IntentBuilder('SetUserIntent').require('set-user'))
	def handle_set_user_intent(self, message):
		self._irc_set_user()

	@intent_handler(IntentBuilder('DebugEnableIntent').require('debug-enable'))
	def handle_debug_enable_intent(self, message):
		self.settings['debug'] = True
		self.speak("Debugging enabled")

	@intent_handler(IntentBuilder('DebugDisableIntent').require('debug-disable'))
	def handle_debug_disable_intent(self, message):
		self.settings['debug'] = False
		self.speak("Debugging disabled")

	def _main_loop(self):
		# Connecttion status: 0 = not connected, 1 = requested, 2 = connected
		connection_state = 0
		# Join status: 0 = not joined, 1 = requested, 2 = joined
		join_statues = 0
		while True:
			sleep(2)
			if connection_state != 0:
				text = ""
				try:
					ready = select.select([irc], [], [], 2)
					if ready[0]:
						text = irc.recv(2040)
				except Exception:
					continue

				for line in text.splitlines():
					if line != "":
						if self.settings['debug']:
							self.speak(str(line))
							pass
		
						# Prevent Timeout
						match = re.search("^PING (.*)$", line, re.M)
						if match != None:
							irc.send('PONG ' + match.group(1) + '\r\n')
							# detect timed out connections
							if int(time()) - self.last_ping > 240:
								self.speak("The connection has timed out. I try to reconnect you")
								self._irc_disconnect(irc, True)
								self._irc_connect(self.settings['server'], self.settings['port'], self.settings['ssl'], self.settings['server-password'], self.settings['user'], self.settings['password'])
								self.speak("You're reconnected")
							self.last_ping = int(time())
	
						# reciving normal messages
						match = re.search("^:(.*)!.*@.* JOIN", line, re.M)
						if match != None:
							if match.group(1) == self.settings['user']:
								join_status = 2
								self.speak("Joined")
							else:
								if self.settings['msg-join']:
									self.speak(match.group(1) + " has joined the channel")
	
						match = re.search("^:(.*)!.*@.* PART", line, re.M)
						if match != None:
							if self.settings['msg-part']:
								self.speak(match.group(1) + " has left the channel")
	
						match = re.search("^:(.*)!.*@.* QUIT", line, re.M)
						if match != None:
							if match.group(1) == self.settings['user']:
								self.speak("You have been disconnected. I try to reconnect you")
								was_joined = join_status
								self._irc_disconnect(irc, True)
								self._irc_connect(self.settings['server'], self.settings['port'], self.settings['ssl'], self.settings['server-password'], self.settings['user'], self.settings['password'])
								self.speak("You are reconnected")
								if was_joined == 2:
									self._irc_join(irc, self.settings['channel'], self.settings['channel-password'])
							elif self.settings['msg-disc']:
								self.speak(match.group(1) + " has disconnected")
	
						match = re.search("^:(.*)!.*@.* PRIVMSG #(.*) :(.*)", line, re.M)
						if match != None:
							self.speak(match.group(1) + " has written in " + match.group(2) + ": " + match.group(3))
	
						match = re.search("^:(.*)!.*@.* NOTICE #.* :(.*)", line, re.M)
						if match != None:
							self.speak(match.group(1) + " has written a notice to " + match.group(2) + ". The notice is: " + match.group(3))
	
						match = re.search("^:(.*)!.*@.* PRIVMSG " + re.escape(self.settings['user']) + " :(.*)$", line, re.M)
						if match != None:
							self.speak(line)
							self.speak(match.group(1) + " has written you a private message: " + match.group(2))

						match = re.search(":(.*)!.*@.* NOTICE " + re.escape(self.settings['user']) + " :(.*)", line)
						if match != None:
							self.speak(match.group(1) + " has written a private notice to you. The notice is: " + match.group(2))


						# reciving status codes
						match = re.search("^:(\S*\.*.\S*) (\d{3}) (.*)", line)
						if match != None:
							code = int(match.group(2))

							if self.settings['debug']:
								self.speak("Return code: " + str(code))

							# This list of handles replies is incomplete
							# We use the MOTD or the missing MOTD message for verify that a connect was successfull
							if code == 372:
								if connection_state != 2:
									connection_state = 2
									self.speak("Connected")

							elif code == 401:
								self.speak("The nickname wasn't found")

							elif code == 422:
								if connection_state != 2:
									connection_state = 2
									self.speak("Connected")

							elif code == 433:
								self.speak("Your nickname is already in use")

							elif code == 464:
								self.speak("It looks, like you password is wrong. Please check it")

							elif code == 465:
								self.speak("You're banned on this server")

						# handling special messages
						match = re.search("^ERROR :Closing link", line)
						if match != None:
							self.speak("The server has closed the connection")
							connection_state = 0
							irc.close()

			cmd = ""
			string = ""

			if self.irc_cmd != "":
				if self.irc_lock == False:
					self.irc_lock = True
					cmd = self.irc_cmd
					string = self.irc_str
					self.irc_cmd = ""
					self.irc_str = ""
					self.irc_lock = False

			if cmd != "":
				# check cmd and take action
				if cmd == "connect":
					# TODO add ability to connect to more than one server
					if connection_state != 2:
						connection_state, irc = self._irc_connect(self.settings['server'], self.settings['port'], self.settings['ssl'], self.settings['server-password'], self.settings['user'], self.settings['password'])
					else:
						self.speak("Already connected")
	
				elif cmd == "join":
					if connection_state == 2:
						join_status = self._irc_join(irc, self.settings['channel'], self.settings['channel-password'])
					else:
						self.speak("Please connect to a server first")
	
				elif cmd == "part":
					if connection_state == 2:
						if join_status == 2:
							join_status = self._irc_part(irc, self.settings['channel'])
						else:
							self.speak("I'm in no channel I could part from")
					else:
						self.speak("Not connected to a server")
	
				elif cmd == "disconnect":
					if connection_state != 0:
						connection_state = self._irc_disconnect(irc)
					else:
						self.speak("I'm to no server connected")
	
					if connection_state == 0:
						join_status = 0
	
				elif cmd == "send":
					if connection_state == 2:
						if join_status == 2:
							self._irc_send(irc, "#" + self.settings['channel'], string)
						else:
							self.speak("Please join a channel first")
					else:
						self.speak("Please connect to a server and join a channel first")


	def _irc_connect(self, server, port, ssl_req, server_password, user, password):

		# check if the default username is used and if so, ask the user to change it
		if user == "dummy|m":
			self.speak("You're using the default user name. Please change it now.")
			changed = False
			while changed == False:
				changed = self._irc_set_user()

			user = self.settings['user']

		irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket

		# Connect
		try:
			if self.settings['debug']:
				self.speak("Server: " + server)
				self.speak("Port: " + str(port))
			irc.settimeout(15)
			irc.connect((server, port))
		except Exception as e:
			self.speak("Unable to connect to server.")
			if self.settings['debug']:
				self.speak("Error: " + str(e))
			return False, irc

		if ssl_req:
			if self.settings['debug']:
				self.speak("Use SSL")
			irc = ssl.wrap_socket(irc)

		irc.setblocking(0)
		if server_password != "":
			irc.send("PASS %s\n" % (password))
		irc.send("USER " + user + " " + user + " " + user + " :IRC via VOICE -> Mycroft\n")
		irc.send("NICK " + user + "\n")
		if password != "":
			irc.send("PRIVMSG nickserv :identify %s %s\r\n" % (user, password))

		self.last_ping = int(time())

		return 1, irc

	def _irc_join(self, irc, channel, channel_password):
		string = "JOIN #"+ channel
		if channel_password != "":
			string = string + " " + channel_password
		irc.send(string +"\n")
		return 1

	def _irc_part(self, irc, channel):
		irc.send("PART #" + channel)
		return 0 # this is the value that's written in `joined`

	def _irc_disconnect(self, irc, quiet=False):
		irc.send("QUIT :Disconnected my mycroft\n")
		irc.close()
		if quiet == False:
			self.speak("Disconnected")
		return 0 # this is the value that's written in `connected`

	def _irc_send(self, irc, to, msg):
		irc.send("PRIVMSG " + to + " :" + msg + "\n")
		self.speak("Message sent")

	def _irc_set_user(self):
		self.speak("Which user name do you want to use?")
		wait_while_speaking()
		response = self.get_response("dummy")
		if response != None:
			response = response.replace(" ", "")
			self.settings['user'] = response
			self.speak("User name changed")
			return True
		self.speak("I didn't understand a user name")
		return False

	def _irc_start_thread(self):
		if self.settings['debug']:
			self.speak("Restart thread")
		self.con_thread = Thread(target=self._main_loop)
		self.con_thread.setDaemon(False)
		self.con_thread.start()

	def stop(self):
		pass

def create_skill():
	return IRCSkill()
