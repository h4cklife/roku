# Roku Remote Control

This application has been developed to remotely control "External Control" enabled Roku
devices. This tool may be used to identify Roku devices on a private network
and perform requests as a "remote" giving the attacker
full control over the device as the owner/operator.

External Control is enabled by default on most Roku devices including Roku enabled
Smart-TVs. Owner should always disable such services on internal network devices if
their is no requirement and need for the service.


## Tested & Verified:

TCL Roku Smart-TV (TCL 32S301-W)


## References

https://sdkdocs.roku.com/display/sdkdoc/External+Control+API


## Usage

------------------------------------------------------------

Target

------------------------------------------------------------

-i --identify                   : Identify Roku devices

-t <target> --target <target>   : Target Roku

-p <port> --port <port>         : Target port

------------------------------------------------------------

Query

------------------------------------------------------------

--deviceinfo                    : Device information

--apps                          : Installed apps/channels

--activeapp                     : Active app

--tvchannels                    : Roku TV channels

--post                          : Manual post request

--get                           : Manual get request

------------------------------------------------------------

Keypress

------------------------------------------------------------

--vu --volumeup                 : Volume up

--vd --volumedown               : Volume down

--vm --volumemute               : Volume mute

--cu --channelup                : Channel up

--cd --channeldown              : Channel down

--home                          : Home screen

--info                          : Info screen

--up                            : Up

--down                          : Down

--left                          : Left

--right                         : Right

--select                        : Select

--rew                           : Rew

--fwd                           : Fwd

--play                          : Play

--poweroff                      : Power off

------------------------------------------------------------

Launch

------------------------------------------------------------

--launch=<id>                   : Launch app by ID

--channel=<num>                 : Launch TV input and chan

--store=<contentID>             : Launch store at contentID Ex: 14=MLB

------------------------------------------------------------

Search

------------------------------------------------------------

--search <keyword>   : Perform a keyword search

--search "pac-man&title=PAC-MAN The Movie" : Perform a keyword and title based search


More @ https://sdkdocs.roku.com/display/sdkdoc/External+Control+API#ExternalControlAPI-searchExamples
