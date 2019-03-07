from wifi import Cell
import time
import re
import subprocess
import os

def _updateWpa(ssid, psk=False):
    wpaPath = '/etc/wpa_supplicant/wpa_supplicant.conf'
    file = open(wpaPath, 'r+')
    content = file.read()
    networkText = re.search('(network=\{{\n.*ssid="{ssid}"\n(.|\n)*?\}})+?'.format(ssid=ssid), content)
    if not networkText and not psk:
        return False
    if networkText:
        networkText=networkText.group(0)
    else:
        networkText = ''
    if not len(content):
        content = """country=FR
update_config=1
ctrl_interface=/var/run/wpa_supplicant\n"""
    if not psk:
        psk=re.search('(?<=psk=").*(?=")', networkText)
        if psk:
            psk = psk.group(0)
        else:
            return False
    content = content.replace(networkText, '')
    content = content.replace("priority=2", "priority=1")
    newNetwork="""network={{
  ssid="{ssid}"
  psk="{psk}"
  priority=2
}}""".format(ssid=ssid, psk=psk)
    os.truncate(wpaPath, 0)
    file.write(content + '\n' + newNetwork)
    return True

def _getValues(network):
    return {
        "ssid": network.ssid,
        "signal": network.signal,
        "quality": network.quality,
        "address": network.address
    }

def getAll(parameters, data):
    networks = []
    for network in Cell.all('wlan0'):
        networks.append(_getValues(network))
    return [{
        "type": "Wifi/getAll",
        "value": networks
    }]

def connect(parameters, data):
    if not 'passkey' in data:
        data['passkey'] = None
    valid = _updateWpa(data['ssid'], data['passkey'])
    answer = {
        "route": "Wifi/connect",
        "ssid": data["ssid"],
        "connected": False
    }
    if not valid:
        return answer
    output = subprocess.check_output('sudo wpa_cli -i wlan0 reconfigure', shell=True).decode('utf8')
    if not 'OK' in output:
        return answer
    # meh
    time.sleep(8)
    current = subprocess.check_output('iwgetid -r', shell=True).decode('utf8')
    print(current)
    if not current:
        return answer
    current = current.replace('\n', '')
    print(current)
    if not current == data['ssid']:
        return answer
    answer['connected'] = True
    return answer
