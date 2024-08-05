"""
Roku Remote Control

This application has been developed to remotely control "External Control" enabled Roku
devices. This tool may be used to identify Roku devices on a private network 
and perform requests as a "remote" giving the attacker
full control over the device as the owner/operator.

External Control is enabled by default on most Roku devices including Roku enabled
Smart-TVs. Owner should always disable such services on internal network devices if 
their is no requirement and need for the service.


Tested & Verified:
    - TCL Roku Smart-TV (TCL 32S301-W)
    - Onn Roku Smart-TV (G814X)


References

https://sdkdocs.roku.com/display/sdkdoc/External+Control+API
"""


__author__ = 'h4cklife'
__copyright__ = 'Copyleft (c) 2017'
__license__ = 'GNU GPL'


import getopt, sys, socket, time, requests, os, socket, signal
import xml.etree.ElementTree as ET

global target_host, target_port, line

target_host = ""
target_port = 8060

"""
Colors
"""
W = '\033[0m'                   # white (normal)
R = '\033[31m'                  # red
G = '\033[32m'                  # green
O = '\033[33m'                  # orange
B = '\033[34m'                  # blue
P = '\033[35m'                  # purple
C = '\033[36m'                  # cyan
K = '[{}*{}]'.format(G, W)      # gui ok
F = '[{}*{}]'.format(R, W)      # gui fail

line = "\n{}-------------------------------------------------------------\n".format(K)

if "raw_input" not in dir(__builtins__):
    raw_input = input


if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])


def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wlo0",
            "wlo1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


def exit_gracefully(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nReally quit? (y/n): ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)


def usage(code):
    """
    usage
    :param code: 

    Displays application usage information
    """
    print('{} ------------------------------------------------------------'.format(K))
    print('{} Target'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} -i --identify                   : Identify Roku devices. Dflt Prt: 8060'.format(K))
    print('{} -t <target> --target <target>   : Target Roku'.format(K))
    print('{} -p <port> --port <port>         : Target port'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} Query'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} --deviceinfo                    : Device information'.format(K))
    print('{} --apps                          : Installed apps/channels'.format(K))
    print('{} --activeapp                     : Active app'.format(K))
    print('{} --tvchannels                    : Roku TV channels'.format(K))
    print('{} --post                          : Manual post request'.format(K))
    print('{} --get                           : Manual get request'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} Keypress'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} --vu --volumeup                 : Volume up'.format(K))
    print('{} --vd --volumedown               : Volume down'.format(K))
    print('{} --vm --volumemute               : Volume mute'.format(K))
    print('{} --cu --channelup                : Channel up'.format(K))
    print('{} --cd --channeldown              : Channel down'.format(K))
    print('{} --home                          : Home screen'.format(K))
    print('{} --info                          : Info screen'.format(K))
    print('{} --up                            : Up'.format(K))
    print('{} --down                          : Down'.format(K))
    print('{} --left                          : Left'.format(K))
    print('{} --right                         : Right'.format(K))
    print('{} --select                        : Select'.format(K))
    print('{} --rew                           : Rew'.format(K))
    print('{} --fwd                           : Fwd'.format(K))
    print('{} --play                          : Play'.format(K))
    print('{} --poweroff                      : Power off'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} Launch'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} --launch=<id>                   : Launch app by ID'.format(K))
    print('{} --channel=<num>                 : Launch TV input and chan'.format(K))
    print('{} --store=<contentID>             : Launch store at contentID Ex: 14=MLB'.format(K))
    print('{} --secretscreen                  : Factory reset, beta mode, USB tests'.format(K))
    print('{} --secretscreen2                 : Hide ads and reset various components'.format(K))
    print('{} --platformscreen                : System operations, network and wireless screens'.format(K))
    print('{} --channelinfo                   : Channel and program info'.format(K))
    print('{} --developersettings             : Developer settings and side loading'.format(K))
    print('{} --hdmisecretscreen              : HDMI secret screen with connection and port modes'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} Search'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} --search <keyword>   : Perform a keyword search'.format(K))
    print('{} --search "pac-man&title=PAC-MAN The Movie" : Perform a keyword and title based search'.format(K))
    print('{} More @ https://sdkdocs.roku.com/display/sdkdoc/External+Control+API#ExternalControlAPI-searchExamples'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} Examples'.format(K))
    print('{} ------------------------------------------------------------'.format(K))
    print('{} python2.7 roku.py -p 8060 -i'.format(K))
    print('{} python2.7 roku.py -t 192.168.1.12 -p 8060 --deviceinfo'.format(K))
    print('{} python2.7 roku.py -t 192.168.1.12 -p 8060 --activeapp'.format(K))
    print('{} python2.7 roku.py -t 192.168.1.12 -p 8060 --home'.format(K))
    print('{} python2.7 roku.py -t 192.168.1.12 -p 8060 --home --down --down --down --down --down --right --right'.format(K))

    print("\n")
    sys.exit(code)


def main(argv):
    """
    main
    :param argv:

    Initial function of the application
    Handle command opts and args in argv and act accordingly
    """
    print("{}{} {} - Roku Command and Control {}".format(line, K, sys.argv[0], line))

    global target_port

    try:
        opts, args = getopt.getopt(argv, "hit:p:", ["target=",
                                                    "port=",
                                                    "help",
                                                    "identify",
                                                    "deviceinfo",
                                                    "apps",
                                                    "activeapp",
                                                    "vu", "volumeup",
                                                    "vd", "volumedown",
                                                    "vm", "volumemute",
                                                    "cu", "channelup",
                                                    "cd","channeldown",
                                                    "home",
                                                    "info",
                                                    "up",
                                                    "down",
                                                    "left",
                                                    "right",
                                                    "select",
                                                    "back",
                                                    "fwd",
                                                    "rev",
                                                    "play"
                                                    "poweroff",
                                                    "search=",
                                                    "launch=",
                                                    "post=",
                                                    "get=",
                                                    "channel=",
                                                    "store=",
                                                    "tvchannels",
                                                    "secretscreen",
                                                    "secretscreen2",
                                                    "platformscreen",
                                                    "channelinfo",
                                                    "developersettings",
                                                    "hdmisecretscreen",
                                                    ])
    except getopt.GetoptError:
        usage(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(0)
            sys.exit()
        elif opt in ("-t", "--target"):
            target_host = str(arg)
        elif opt in ("-p", "--port"):
            target_port = int(arg)
        elif opt in ("-i", "--identify"):
            print("{} Identifying Roku devices on private network....".format(K))
            identify(target_port)
            sys.exit(0)
        elif opt not in ("-i", "--identify") and len(sys.argv) < 6:
            usage(2)
            sys.exit(0)
        elif opt in ("--deviceinfo"):
            print("{} Requesting device information...".format(K))
            device_information(target_host, target_port)
        elif opt in ("--apps"):
            print("{} Requesting installed applications and channels...".format(K))
            get_apps(target_host, target_port)
        elif opt in ("--activeapp"):
            print("{} Requesting active application...".format(K))
            get_running_app(target_host, target_port)
        elif opt in ("--vu", "--volumeup"):
            print("{} Volume up...".format(K))
            post(target_host, target_port, 'keypress/VolumeUp')
        elif opt in ("--vd", "--volumedown"):
            print("{} Volume down....".format(K))
            post(target_host, target_port, 'keypress/VolumeDown')
        elif opt in ("--vm", "--volumemute"):
            print("{} Volume mute...".format(K))
            post(target_host, target_port, 'keypress/VolumeMute')
        elif opt in ("--cu", "--channelup"):
            print("{} Changing channel > up....".format(K))
            post(target_host, target_port, 'keypress/ChannelUp')
        elif opt in ("--cd", "--channeldown"):
            print("{} Changing channel > down....".format(K))
            post(target_host, target_port, 'keypress/ChannelDown')
        elif opt in ("--home"):
            print("{} Sending TV to Home screen....".format(K))
            post(target_host, target_port, 'keypress/Home')
        elif opt in ( "--info"):
            print("{} Sending TV to Info screen....".format(K))
            post(target_host, target_port, 'keypress/Info')
        elif opt in ("--up"):
            print("{} Sending Up command....".format(K))
            post(target_host, target_port, 'keypress/Up')
        elif opt in ("--down"):
            print("{} Sending down command....".format(K))
            post(target_host, target_port, 'keypress/Down')
        elif opt in ("--left"):
            print("{} Sending Left command....".format(K))
            post(target_host, target_port, 'keypress/Left')
        elif opt in ("--right"):
            print("{} Sending Right command....".format(K))
            post(target_host, target_port, 'keypress/Right')
        elif opt in ( "--select"):
            print("{} Sending Select command....".format(K))
            post(target_host, target_port, 'keypress/Select')
        elif opt in ("--back"):
            print("{} Sending Back command....".format(K))
            post(target_host, target_port, 'keypress/Back')
        elif opt in ("--fwd"):
            print("{} Sending Fwd command....".format(K))
            post(target_host, target_port, 'keypress/Fwd')
        elif opt in ("--rev"):
            print("{} Sending Rew command....".format(K))
            post(target_host, target_port, 'keypress/Rev')
        elif opt in ("--play"):
            print("{} Sending Play command....".format(K))
            post(target_host, target_port, 'keypress/Play')
        elif opt in ("--poweroff"):
            print("{} Power off....".format(K))
            post(target_host, target_port, 'keypress/PowerOff')
        elif opt in ("--launch"):
            print("{} Launching Application by ID: {}....".format(K, arg))
            post(target_host, target_port, 'launch/{}'.format(arg))
        elif opt in ("--search"):
            print("{} Searching for {}....".format(K, arg.encode('utf-8')))
            post(target_host, target_port, 'search/browse?keyword={}'.format(arg.encode('utf-8')))
        elif opt in ("--post"):
            print("{} Performing post {}....".format(K, arg.encode('utf-8')))
            post(target_host, target_port, '{}'.format(arg.encode('utf-8')))
        elif opt in ("--get"):
            print("{} Performing get {}....".format(K, arg.encode('utf-8')))
            print(get(target_host, target_port, '{}'.format(arg.encode('utf-8')).encode('utf-8')))
        elif opt in ("--channel"):
            print("{} Loading TV Input and surfing to channel....".format(K))
            # Home Home Home Home Up Up Right Left Right Left Right
            post(target_host, target_port, 'launch/tvinput.dtv?ch={}'.format(arg.encode('utf-8')))
        elif opt in ("--store"):
            print("{} Loading Store at contentID App....".format(K))
            # Home Home Home Home Up Up Right Left Right Left Right
            post(target_host, target_port, 'launch/11?contentID={}'.format(arg.encode('utf-8')))
        elif opt in ("--tvchannels"):
            print("{} Requesting available TV channels...".format(K))
            get_tv_channels(target_host, target_port)
        elif opt in ("--secretscreen"):
            print("{} Launching secret screen...".format(K))
            secret_screen(target_host, target_port)
        elif opt in ("--secretscreen2"):
            print("{} Launching secret screen 2...".format(K))
            secret_screen_two(target_host, target_port)
        elif opt in ("--platformscreen"):
            print("{} Launching platform screen...".format(K))
            platform_screen(target_host, target_port)
        elif opt in ("--channelinfo"):
            print("{} Launching channel info screen...".format(K))
            channel_info(target_host, target_port)
        elif opt in ("--developersettings"):
            print("{} Launching developer settings...".format(K))
            developer_settings(target_host, target_port)
        elif opt in ("--hdmisecretscreen"):
            print("{} Launching HDMI secret screen....".format(K))
            hdmi_secret_screen(target_host, target_port)


    print("\n")
    sys.exit(0)


def post(target_host, target_port, query):
    """
    post
    :param target_host: 
    :param target_port: 
    :param query: 
    :return: 
    
    Perform a POST request to the Roku device
    """
    r = requests.post("http://{}:{}/{}".format(target_host, target_port, query))
    print("{} {} - {}".format(K, query, r.reason))
    return True


def get(target_host, target_port, query):
    """
    get
    :param target_host: 
    :param target_port: 
    :param query: 
    :return: 
    
    Perform a GET request to the Roku device
    """
    r = requests.get("http://{}:{}/{}".format(target_host, target_port, query))
    print("{} {}!\n".format(K, r.reason))
    #print("{}".format(r.text))
    return r.text


def identify(target_port=8060):
    """
    identify
    :return: 
    
    Identify Roku devices on the private network
    Currently sending device-info requests instead of using SSDP
    """
    lan = get_lan_ip()
    n = 3
    groups = lan.split('.')
    lan2 = '.'.join(groups[:n]), '.'.join(groups[n:])
    for oct in range(1, 255, 1):
        try:
            print("{} Trying {}".format(K, lan2[0]+"."+str(oct)))
            r = requests.get("http://{}:{}/query/device-info".format('192.168.2.'+str(oct), target_port))
            print("{} Identified Roku device {}....".format(K, lan2[0]+"."+str(oct)))
        except KeyboardInterrupt:
            print("Rawr..ok..ok..quitting!")
            sys.exit(1)
        except Exception:
            #print("{} Check failed for {}....".format(F, lan2[0] + "." + str(oct)))
            pass


def get_running_app(target_host, target_port):
    """
    get_running_app
    :param target_host: 
    :param target_port: 
    :return: 
    
    Display the running Application/Channel on the Roku device
    """
    try:
        resp = get(target_host, target_port, 'query/active-app')
        root = ET.fromstring(resp)
        for child in root:
            print("{} ID: {}".format(K, child.attrib['id']))
            print("{} App: {}".format(K, child.text.encode('utf-8')))
            print("{} Type: {}".format(K, child.attrib['type']))
            print("{} Version: {}".format(K, child.attrib['version']))
            print("\n")
    except Exception:
        print("{} {}".format(F, "No applications are currently loaded! Likely using HDMI / Cable / Antenna\n"))

    return True


def get_apps(target_host, target_port):
    """
    get_apps
    :param target_host: 
    :param target_port: 
    :return: 
    
    Display a list of Apps & Channels installed on the Roku device
    """
    try:
        resp = get(target_host, target_port, 'query/apps')
        root = ET.fromstring(resp.encode('utf-8'))
        for child in root:
            try:
                print("{} ID: {}".format(K, child.attrib['id']))
                print("{} App: {}".format(K, child.text.encode('utf-8')))
                print("{} Type: {}".format(K, child.attrib['type']))
                print("{} Version: {}".format(K, child.attrib['version']))
                print("\n")
            except Exception:
                print("{} {}".format(F, "Error printing application...\n"))

    except Exception:
        print("{} {}".format(F, "Error returning installed applications and channels...\n"))

    return True


def get_tv_channels(target_host, target_port):
    """
    get_tv_channels
    :param target_host: 
    :param target_port: 
    :return: 

    Display a list of available tv channels
    """
    try:
        resp = get(target_host, target_port, 'query/tv-channels')
        root = ET.fromstring(resp.encode('utf-8'))
        for child in root:
            for chi in child:
                try:
                    print("{} {}: {}".format(K, chi.tag.encode('utf-8'), chi.text.encode('utf-8')))
                except Exception:
                    print("{} {}".format(F, "Error printing channel...\n"))
            print("\n")
    except Exception:
        print("{} {}".format(F, "Error returning channels...\n"))

    return True


def device_information(target_host, target_port):
    """
    device_information
    :param target_host: 
    :param target_port: 
    :return: 
    
    Display Roku device information
    """
    try:
        resp = get(target_host, target_port, 'query/device-info')
        root = ET.fromstring(resp.encode('utf-8'))
        for child in root:
            print("{} {}: {}".format(K, child.tag, child.text))
        print("\n")
    except Exception:
        print("{} {}".format(F, "Could not return device information...\n"))

    return True


def secret_screen(target_host, target_port):
    # Send home and wait 5 seconds before we begin
    post(target_host, target_port, 'keypress/Home')
    time.sleep(5)
    # Home x5 - FF x3 - RW x2
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Fwd')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Fwd')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Fwd')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Rev')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Rev')


def secret_screen_two(target_host, target_port):
    # Send home and wait 5 seconds before we begin
    post(target_host, target_port, 'keypress/Home')
    time.sleep(5)
    # Home x5 - Up - Right - Down - Left - Up
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Right')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Down')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Left')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')


def platform_screen(target_host, target_port):
    # Send home and wait 5 seconds before we begin
    post(target_host, target_port, 'keypress/Home')
    time.sleep(5)
    # Home x5 - FF - Play - RW - Play - FF
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Fwd')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Play')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Rev')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Play')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Fwd')


def channel_info(target_host, target_port):
    # Send home and wait 5 seconds before we begin
    post(target_host, target_port, 'keypress/Home')
    time.sleep(5)
    # Home (x3), Up (x2), Left, Right, Left, Right, Left
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Left')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Right')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Left')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Right')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Left')
    time.sleep(.5)


def developer_settings(target_host, target_port):
    # Send home and wait 5 seconds before we begin
    post(target_host, target_port, 'keypress/Home')
    time.sleep(5)
    # Home (x3), Up (x2), Right, Left, Right, Left, Right.
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Right')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Left')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Right')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Left')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Right')
    time.sleep(.5)


def hdmi_secret_screen(target_host, target_port):
    # Send home and wait 5 seconds before we begin
    post(target_host, target_port, 'keypress/Home')
    time.sleep(5)
    # Home (x5) - Down - Left - Up (x3)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Home')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Down')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Left')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')
    time.sleep(.5)
    post(target_host, target_port, 'keypress/Up')
    time.sleep(.5)


if __name__ == "__main__":
    """
    init

    Initialize the script application's main function
    """
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    main(sys.argv[1:])

