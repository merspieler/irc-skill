from threading import Thread
from time import sleep
import socket
import socks
import ssl

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
		self.settings['server'] = "irc.esper.net"
		self.settings['port'] = 6667
		self.settings['channel'] = "dummy"
		self.settings['user'] = "dummy|m"
		self.settings['password'] = ""
		self.settings['ssl'] = False


		self.con_thread = Thread(target=self._main_loop)
		self.con_thread.setDaemon(True)
		self.con_thread.start()

		if self.settings['proxy'] != "":
			socks.set_default_proxy(socks.SOCKS5, self.settings['proxy'], self.settings['proxy-port'], True, 'user','passwd')
			socket.socket = socks.socksocket


	@intent_handler(IntentBuilder('ConnectIntent').require('connect'))
	def handle_connect_intent(self, message):
		if self.settings['ssl']:
			irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
			irc = ssl.wrap_socket(irc_C)
		else:
			irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket

		# Connect
		try:
			irc.connect((self.settings['server'], self.settings['port']))
		except Exception, e:
			self.speak("Unable to connect to server")

		irc.setblocking(False)
#		irc.send("PASS %s\n" % (password))
		irc.send("USER " + self.settings['user'] + " " + self.settings['user'] + " " + self.settings['user'] + " :IRC via VOICE -> Mycroft\n")
		irc.send("NICK " + self.settings['user'] + "\n")
#		irc.send("PRIVMSG nickserv :identify %s %s\r\n" % (botnick, password))
		irc.send("JOIN #"+ self.settings['channel'] +"\n")

		self.speak("Connected")

	def _main_loop(self):
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
