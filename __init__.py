from threading import Thread
from time import sleep
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
		self.settings['server'] = "irc.flightgear.org"
		self.settings['port'] = 6667
		self.settings['channel'] = "mycroft"
		self.settings['channel-password'] = ""
		self.settings['user'] = "dummy|m"
		self.settings['password'] = ""
		self.settings['ssl'] = False

		# IPC for comunicating between threads
		self.irc_lock = False
		self.irc_cmd = ""
		self.irc_str = ""

		if self.settings['proxy'] != "":
			socks.set_default_proxy(socks.SOCKS5, self.settings['proxy'], self.settings['proxy-port'], True, 'user','passwd')
			socket.socket = socks.socksocket

	def initialize(self):
		self.con_thread = Thread(target=self._main_loop)
		self.con_thread.setDaemon(False)
		self.con_thread.start()

	@intent_handler(IntentBuilder('ConnectIntent').require('connect'))
	def handle_connect_intent(self, message):
		# TODO ability to connect to different server
		if self.con_thread.isAlive() == False:
			self.speak("Restart thread")
			self.con_thread.start()
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
			self.speak("Restart thread")
			self.con_thread.start()
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
			self.speak("Restart thread")
			self.con_thread.start()
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
			self.speak("Restart thread")
			self.con_thread.start()
		if self.irc_lock == False:
			self.speak("Disconnecting")
			self.irc_lock == True
			self.irc_cmd = "disconnect"
			self.irc_str = ""
			self.irc_lock = False

	def _main_loop(self):
		connected = False
		joined = False
		while True:
			sleep(2)
			if connected:
				text = ""
				try:
					ready = select.select([irc], [], [], 2)
					if ready[0]:
						text = irc.recv(2040)
				except Exception:
					continue
	
				if text != "":
#					self.speak(text)
	
					# Prevent Timeout
					match = re.search("PING (.*)", text)
					if match != None:
						irc.send('PONG ' + match.group(1) + '\r\n')

					match = re.search(":(.*)!.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} QUIT", text)
					if match != None:
						self.speak(match.group(1) + " has disconnected")

					match = re.search(":(.*)!.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} JOIN", text)
					if match != None:
						if match.group(1) != self.settings['user']:
							self.speak(match.group(1) + " has joined the channel")

					match = re.search(":(.*)!.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} PART", text)
					if match != None:
						self.speak(match.group(1) + " has left the channel")

					match = re.search(":(.*)!.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} QUIT", text)
					if match != None:
						self.speak(match.group(1) + " has disconnected")

					match = re.search(":(.*)!.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} PRIVMSG #.* :(.*)", text)
					if match != None:
						self.speak(match.group(1) + " has written in " + match.group(2) + ": " + match.group(3))

# TODO fix
#					match = re.search(":(.*)!.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} PRIVMSG " + self.settings['user'] + " :(.*)", text)
#					if match != None:
#						self.speak(match.group(1) + " has written you a private message: " + match.group(2))

					match = re.search(":(.*)!.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} NOTICE #.* :(.*)", text)
					if match != None:
						self.speak(match.group(1) + " has written a notice to " + match.group(2) + ". The notice is: " + match.group(3))

# TODO fix
#					match = re.search(":(.*)!.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} NOTICE " + self.settings['user'] + " :(.*)", text)
#					if match != None:
#						self.speak(match.group(1) + " has written a private notice to you. The notice is: " + match.group(2))

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
					if connected == False:
						connected, irc = self._irc_connect(self.settings['server'], self.settings['port'], self.settings['ssl'], self.settings['user'], self.settings['password'])
					else:
						self.speak("Already connected")
	
				elif cmd == "join":
					if connected:
						joined = self._irc_join(irc, self.settings['channel'], self.settings['channel-password'])
					else:
						self.speak("Please connect to a server first")
	
				elif cmd == "part":
					pass
	
				elif cmd == "disconnect":
					if connected:
						connected = self._irc_disconnect(irc)
					else:
						self.speak("I'm to no server connected")
	
					if connected == False:
						joined = False
	
				elif cmd == "send":
					pass

	def _irc_connect(self, server, port, ssl_req, user, password):
		if ssl_req:
			irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
			irc = ssl.wrap_socket(irc_C, cert_reqs=ssl.CERT_NONE)
		else:
			irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket

		# Connect
		try:
			irc.connect((server, port))
		except Exception, e:
			self.speak("Unable to connect to server.")
			return False, irc

		irc.setblocking(0)
		if password != "":
			irc.send("PASS %s\n" % (password))
		irc.send("USER " + user + " " + user + " " + user + " :IRC via VOICE -> Mycroft\n")
		irc.send("NICK " + user + "\n")
#		irc.send("PRIVMSG nickserv :identify %s %s\r\n" % (botnick, password))

		self.speak("Connected")
		return True, irc

	def _irc_join(self, irc, channel, channel_password):
		# TODO add steps to be able to use a pw
		irc.send("JOIN #"+ channel +"\n")
		self.speak("Channel " + channel + " joined")
		return True

	def _irc_part(self):
		pass

	def _irc_disconnect(self, irc):
		irc.send("QUIT :Disconnected my mycroft\n")
		irc.close()
		self.speak("Disconnected")
		return False # this is the value that's written in `connected`

	def _irc_send(self, irc, to, msg):
		pass

	def stop(self):
		pass

def create_skill():
	return IRCSkill()
"""
### Tail
tail_files = [
    '/tmp/file-to-tail.txt'
]


print "Establishing connection to [%s]" % (server)


tail_line = []
for i, tail in enumerate(tail_files):
    tail_line.append('')


while True:
    time.sleep(2)

    # Tail Files
    for i, tail in enumerate(tail_files):
        try:
            f = open(tail, 'r')
            line = f.readlines()[-1]
            f.close()
            if tail_line[i] != line:
                tail_line[i] = line
                irc.send("PRIVMSG %s :%s" % (channel, line))
        except Exception as e:
            print "Error with file %s" % (tail)
            print e

    try:
        text=irc.recv(2040)
        print text

        # Prevent Timeout
        if text.find('PING') != -1:
            irc.send('PONG ' + text.split() [1] + '\r\n')
    except Exception:
        continue
"""		
