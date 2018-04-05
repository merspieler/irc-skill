# Skill Testing Template
The purpose of this template is to help a Mycroft Community Skill Developer outline how a Community Member can install, configure, and test the Skill. This template is aimed at making Skills easier to test, and thereby increasing the quality of Skills deployed. 

# IRC skill

* Platform <!-- which platform is the test being run on? ie Picroft, Mark 1, Linux -->
* Device version <!-- what Mycroft version is the device running, ie 18.02 -->
* Who <!-- who is running the test -->
* Datestamp <!-- time and date -->
* Language and dialect of tester <!-- ie "English, Australian" so that we can identify any key language issues -->

# How to install Skill
To install just say `Hey Mycroft, install irc skill`

# Steps to test the Skill
_Note that sometimes mycroft might not understand you correct. Please check that before you open an issue_

_Note that the default server is `irc.freenode.net` which connects to the freenode network. The default channel is `#mycroft`_

1. Connect to a server:
	* Say `connect to irc`
	* If this is the first time you run this skill, the skill will ask you for username. Choose a short, if possible one word, user name.
	* The skill response with `Connecting` and with `Connected` as soon as a connection is established.

2. Join a channel:
	* Say `join irc channel`
	* The skill responses with `Joining` and with `Joined` as soon as the join was successfull where `<channel>` should be `mycroft`right now.

3. Sending and reciving messages:
	* Connect with a different irc client to the network or use [this link](https://kiwiirc.com/client/irc.freenode.net:+6669/mycroft) to open one in your browser.
	* Say `send irc message` (For me, mycroft has problems to understand the send word correctly)
	* The skill will ask you for a message. You can simply say `Hi` to the people in the channel.
	* In your client/browser, check if the message appears.
	* Write an aswer in your client/browser.
	* The skill should response with `<user> has writtent in mycroft: <your text>` where  `<user>` is the username in your client and `<your text>` is what you've typed in your client.

4. Disconnect:
	* Say `Disconnect from irc`
	* The skill should response with `Disconnecting` and `Disconnected`.

You know now the basics of how to use this skill. Play with it a bit around (settings can't be changed by voice yet) or just have fun chatting with your mycroft mates in `#mycroft` on freenode.

If you encounter any issue please try to reproduce with debug mode enabled.  
Debug mode can be turned on by saying `enable irc debug`.

_**Note** This will make the skill almost unuseable via voice (the client will spam you with information).  Please use the console instead._

To exit debug mode say `disable irc debug`
