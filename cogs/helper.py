import configparser
from pathlib import Path

global token, prefix, botid, channelid, ownerid, responsechance, debug, settingsfile, cachename, maxlines, togpu, modelfolder, activesettingsvar, custommsg

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
    togpu = config.getboolean('aiSettings', 'togpu')
    globals().update(tokenlib)
    globals().update(settingslib)
    globals().update(ailib)
    togpu = config.getboolean('aiSettings', 'togpu')
    settingsfile = config.get('settings', 'settingsfile')


def activesettings():
    config.read(activesettingsvar)
    tokenlib = dict(config.items('token'))
    settingslib = dict(config.items('settings'))
    ailib = dict(config.items('aiSettings'))
    globals().update(tokenlib)
    globals().update(settingslib)
    globals().update(ailib)


def showsettings():
    print("=================================================================")
    print("The Following settings have been loaded:")
    print(" ")
    print("[settings]")
    print(f"prefix : {prefix}")
    print(f"botid : {botid}")
    print(f"channelid : {channelid}")
    print(f"responseChance : {responsechance}")
    print(f"debug : {debug}")
    print(f"settingsfile : {settingsfile}")
    print(" ")
    print("[aiSettings]")
    print(f"cachename : {cachename}")
    print(f"maxlines : {maxlines}")
    print(f"togpu : {togpu}")
    print(f"modelfolder : {modelfolder}")
    print("=================================================================")


def savesettings(settingsfile="config.ini", modelfolder="trained_model", togpu="0"):
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
    config.set('aiSettings', 'modelfolder', f'{modelfolder}')
    config.set('aiSettings', 'togpu', togpu)
    with open(settingsfile, 'w') as settingsfile:
        config.write(settingsfile)
