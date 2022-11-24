import configparser
from pathlib import Path

global token, prefix, botid, channelid, ownerid, responsechance, debug, settingsfile, cachename, maxlines
global togpu, modelfolder, activesettingsvar, custommsg, configname, togpubool, debugbool, activitytype
global activitytext, activitystatus, discstatus, activitylabel, loglevelvar, customauthorid

config = configparser.ConfigParser()


def opensettings(settingsfile="config.ini"):
    filecheck = Path(f"./{settingsfile}")
    if not filecheck.exists():
        print("couldn't find the settings file, cancelling..")
        return
    config.read(settingsfile)
    config.set('settings', 'settingsfile', f'{settingsfile}')
    tokenlib = dict(config.items('token'))
    settingslib = dict(config.items('settings'))
    ailib = dict(config.items('aiSettings'))
    boollib = dict(config.items('boolvalues'))
    togpu = config.getboolean('aiSettings', 'togpu')
    globals().update(tokenlib)
    globals().update(settingslib)
    globals().update(ailib)
    globals().update(boollib)
    settingsfile = config.get('settings', 'settingsfile')


def activesettings():
    config.read(activesettingsvar)
    tokenlib = dict(config.items('token'))
    settingslib = dict(config.items('settings'))
    ailib = dict(config.items('aiSettings'))
    boollib = dict(config.items('boolvalues'))
    globals().update(tokenlib)
    globals().update(settingslib)
    globals().update(ailib)
    globals().update(boollib)


def showsettings():
    togpubool = config.getboolean('aiSettings', 'togpu')
    debugbool = config.getboolean('settings', 'debug')
    print("=================================================================")
    print("The Following settings have been loaded:")
    print(" ")
    print("--------------")
    print("Bot Settings:")
    print("--------------")
    print(f"prefix : {prefix}")
    print(f"botid : {botid}")
    print(f"channelid : {channelid}")
    print(f"responseChance : {responsechance}")
    print(f"debug : {debugbool}")
    print(f"settingsfile : {settingsfile}")
    print(f"activity : {activitystatus} | {activitytype} {activitytext}")
    print(" ")
    print("--------------")
    print("AI Settings:")
    print("--------------")
    print(f"cachename : {cachename}")
    print(f"maxlines : {maxlines}")
    print(f"togpu : {togpubool}")
    print(f"modelfolder : {modelfolder}")
    print(" ")
    print("=================================================================")


def savesettings(settingsfile="config.ini", cachename=None, modelfolder=None, togpu=None, debug=None, token=None):
    filecheck = Path(f"./{settingsfile}")
    if not filecheck.exists():
        try:
            with open('config.ini', 'r') as firstfile, open(f'{settingsfile}', 'a') as secondfile:
                for line in firstfile:
                    secondfile.write(line)
        except:
            print("couldn't save a new settings file, cancelling..")
            return
    config.read(settingsfile)
    config.set('settings', 'settingsfile', f'{settingsfile}')
    if cachename:
        config.set('aiSettings', 'cachename', f'{cachename}')
    if modelfolder:
        config.set('aiSettings', 'modelfolder', f'{modelfolder}')
    if togpu:
        config.set('aiSettings', 'togpu', togpu)
        togpubool = config.getboolean('aiSettings', 'togpu')
        config.set('boolvalues', 'togpubool', f'{togpubool}')
    if debug:
        config.set('settings', 'debug', debug)
        debugbool = config.getboolean('settings', 'debug')
        config.set('boolvalues', 'debugbool', f'{debugbool}')
    if token:
        config.set('token', 'token', token)
    with open(settingsfile, 'w') as settingsfile:
        config.write(settingsfile)
