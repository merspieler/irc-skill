## irc-skill
Basic IRC client

## Description 
Mycroft skill that lets you use IRC via voice commands.

This skill is not considered done.
_NOTE_: Developent has been currently stoped due to personal reasons. Merge Requests will still be accepted.

## Requirements
* `pysocks`

## Examples
### Normal use
_Currently available commands_
* "connect to irc" Connect to the server.
* "join irc channel" Join the channel.
* "send irc message" Send a message.
* "part from irc channel" Leave the channel.
* "disconnect from irc server" Disconnect from the server.

### Configurational use
* "enable irc debug" To enter debug mode.
* "disable irc debug" To leave debug mode.

_**Note** settings are set in the `settings.json` file. Right now it's only possible to join one server and one channel at a time._
### Configuration
_Configuration via voice isn't supported yet_

Supported configuration options in the `settings.json` file:
* Server
  * `server`: The adress of the server.
  * `port`: The used port.
  * `ssl`: If SSL should be used (can be `True` or `False`)
  * `server-password`: The password for the server. **Note** This is only needed for password protected servers. For user password, see below.
* Proxy (Only socks proxys are supported)
  * `proxy`: The proxy adress. If empty, no proxy is used.
  * `proxy-port`: The port of the proxy.
  * `proxy-user`: The user to authentificate with. _Only needed if authentification is required for the proxy._
  * `proxy-passwd`: The password to authentificate with.
* User
  * `user`: The username.
  * `password`: Password to use when the username is registered.
* Channel
  * `channel`: The channel to join.
  * `channel-password`: The channel password if required. _**Note** This feature isn't implemented yet._


_Use the debuging mode only on the console. This will not work well for normal useage._
* "Enable irc debug" Enables debug mode. This will print useful information for debugging and **every** message recived. This includes messages like the `PING` message.
* "Disable irc debug" Disables debug mode and goes back to normal output.

## Credits 
