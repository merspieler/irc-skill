from threading import Thread
from time import sleep
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

LOGGER = getLogger(__name__)

class IRCSkill(MycroftSkill):
	def __init__(self):
		super(IRCSkill, self).__init__()
		# TODO make them configureable
		# TODO make them into lists
		# options
		self.settings['proxy'] = "127.0.0.1"
		self.settings['proxy-port'] = 9050
		self.settings['proxy-user'] = ""
		self.settings['proxy-passwd'] = ""
		self.settings['server'] = "irc.flightgear.org"
		self.settings['port'] = 6667
		self.settings['channel'] = "mycroft"
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
		if self.con_thread.isAlive() == False:
			self.speak("Restart thread")
			self.con_thread.start()
		if self.irc_lock == False:
			self.speak("Connecting")
			self.irc_lock == True
			self.irc_cmd = "connect"
			self.irc_str = ""# TODO !!!!!!!!!!!!!!
			self.irc_lock = False

	def _main_loop(self):
		connected = False
		while True:
			sleep(2)
			if connected:
				text = ""
				try:
					text = irc.recv(2040)
				except Exception:
					continue
	
				if text != "":
					self.speak(text)
	
					# Prevent Timeout
					match = re.search("PING (.*)", text, re.I)
					if match != None:
						irc.send('PONG ' + match.group(1) + '\r\n')

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

			# check cmd and take action
			if cmd == "connect":
				connected, irc = self._irc_connect(self.settings['server'], self.settings['port'], self.settings['ssl'], self.settings['user'], self.settings['password'])
				connected = True
			elif cmd == "join":
				pass
			elif cmd == "part":
				pass
			elif cmd == "send":
				pass

	def _irc_connect(self, server, port, ssl_req, user, password):
		self.speak("test ssl")
		if ssl_req:
			irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
			irc = ssl.wrap_socket(irc_C, cert_reqs=ssl.CERT_NONE)
		else:
			irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket

		self.speak("test con")
		# Connect
		try:
			irc.connect((server, port))
		except Exception, e:
			self.speak("Unable to connect to server.")
			return False, irc

		self.speak("test auth")
		irc.setblocking(0)
		if password != "":
			irc.send("PASS %s\n" % (password))
		irc.send("USER " + user + " " + user + " " + user + " :IRC via VOICE -> Mycroft\n")
		irc.send("NICK " + user + "\n")
#		irc.send("PRIVMSG nickserv :identify %s %s\r\n" % (botnick, password))

		self.speak("Connected")
		return True, irc

	def _irc_join(self, channel):
		irc.send("JOIN #"+ channel +"\n")

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
