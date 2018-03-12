from threading import Thread
from time import sleep
import socket
import socks
import ssl

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
		self.settings['server'] = "irc.darkfasel.net"
		self.settings['port'] = 6697
		self.settings['channel'] = "ccc"
		self.settings['user'] = "dummy|m"
		self.settings['password'] = ""

		socks.set_default_proxy(socks.SOCKS5, self.settings['proxy'], self.settings['proxy-port'], True, 'user','passwd')
		socket.socket = socks.socksocket


"""
### Tail
tail_files = [
    '/tmp/file-to-tail.txt'
]

irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
irc = ssl.wrap_socket(irc_C)

print "Establishing connection to [%s]" % (server)
# Connect
irc.connect((server, port))
irc.setblocking(False)
irc.send("PASS %s\n" % (password))
irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :meLon-Test\n")
irc.send("NICK "+ botnick +"\n")
irc.send("PRIVMSG nickserv :identify %s %s\r\n" % (botnick, password))
irc.send("JOIN "+ channel +"\n")


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
