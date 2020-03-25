#!/usr/bin/python3

import requests
from lxml import html
import subprocess as sp
import re
import sys
import logging
import time

def check_is_residhotel():
    try:
        output = sp.check_output(['iwgetid']).decode()
        pattern = re.compile('(\w*)\s+ESSID:"(.*)"')
        iface, ssid = pattern.match(output).groups()
        return (ssid == 'Wifipass' and iface == 'wlp2s0')
    except Exception as e:
        logging.debug(e)



def check_internet():
    url = 'http://www.google.com/'
    timeout = 5
    try:
        response = requests.get(url, timeout=timeout)
        tree = html.fromstring(response.text)
        title = tree.find('.//title').text
        if title != 'Google':
            return False
        return True
    except requests.ConnectionError as e:
        logging.info("Connectivity issues detected.")
        logging.debug(e)
    return False


def login_routine():
    with requests.Session() as session:
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'http://passman02.wifipass.org',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': 'http://passman02.wifipass.org/w2p/login-url-real.php?id=resid_le_royal&domain=controleur.wifipass.org',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        session.headers.update(headers)
        params = (
            ('id', 'resid_le_royal'),
            ('domain', 'controleur.wifipass.org'),
            ('mac', 'A1-E2-F5-E1-10-78')
        )

        # The following two requests seem to be redundant.

        # welcome = 'http://passman02.wifipass.org/w2p/login-url.php'
        # response = session.get(welcome, params=params)
        # welcome_real = 'http://passman02.wifipass.org/w2p/login-url-real.php'
        # response = session.get(welcome_real, params=params)

        registration = 'http://passman02.wifipass.org/w2p/formulaire_fin.php?id=resid_le_royal&domain=controleur.wifipass.org'
        data = {
            'registration[firstname]' : 'Darth',
            'registration[lastname]' : 'Vader',
            'registration[email]' : 'darth.vader@death.star',
            'registration[id1]' : '1',
            'registration[id2]' : '211',
            'registration[newsLetterType]' : 'PASSMAN'
        }

        response = session.post(registration, params=params, data=data)

        def get_login_data(response):
            tree = html.fromstring(response.text)
            form, *whatever = tree.xpath('//form')
            inputs = form.xpath('//input')
            login_data = {}
            for _input in inputs:
                key = _input.get('name')
                value = _input.get('value')
                login_data[key] = value
            return login_data

        login_data = get_login_data(response)
        login_url = 'http://controleur.wifipass.org/goform/HtmlLoginRequest'
        response = session.post(login_url, data=login_data)
        logging.debug('Login status: {}'.format(response.status_code))


if __name__ == '__main__':
    logfile = '/var/log/residhotel-login-dispatch.log'
    logging.basicConfig(filename=logfile, level=logging.INFO,
            format='%(asctime)s %(message)s')
    iface, status = sys.argv[1], sys.argv[2]
    
    def guarded_login():
        logging.info("Attempting relogin.")
        try:
            login_routine()
        except Exception as e:
            logging.debug(e)
        time.sleep(5)

    if iface == 'wlp2s0':
        logging.info("iface ({}) -> event ({})".format(iface, status))
        if check_is_residhotel():
            guarded_login()

    if status == 'connectivity-change':
        if check_is_residhotel():
            logging.info("{} on Wifipass".format(status))
        while not check_internet():
            guarded_login()
        logging.info("connection succeeded.")


