import json
import requests as r
import subprocess
import shlex
from string import ascii_letters, digits
from random import choice
from time import sleep

CONFIG_PATH = "./config.json"
RULES_PATH = "./rules.json"
PASSWORD_PATH = "./password"
BASE = 'http://{}:4444/api{}'


def get_password():
    password = None
    try:
        with open(PASSWORD_PATH, "r") as f:
            password = f.readline()
    except:
        password = ''.join(choice(ascii_letters + digits) for i in range(64))
        with open(PASSWORD_PATH, "w") as f:
            f.writelines(password)
    return password


def start_firegex(with_pw=False):
    cmd = '/usr/bin/env python3 start.py start --build'
    if with_pw:
        cmd += f' --psw-no-interactive {get_password()}'
    subprocess.check_call(shlex.split(cmd),
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    sleep(2)


def stop_firegex():
    subprocess.check_call(shlex.split(f'/usr/bin/env python3 start.py stop'),
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # subprocess.check_call(shlex.split(f'docker volume rm firegex_firegex_data'),
    #                       stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def print_fixed_width(s):
    print(s.ljust(60), end='')


def setup():
    with open(CONFIG_PATH, "r") as f:
        js = json.load(f)
    with open(RULES_PATH, "r") as f:
        rules = json.load(f)
    try:
        print("The password is: " + get_password())
        print_fixed_width("Starting firegex ... ")
        start_firegex(True)
        print("OK")

        ip = js['team_ip']
        challenges = js['challenges']

        print_fixed_width("Logging in to retrieve access token ...")
        data = r.post(BASE.format(ip, '/login'), data={
            'username': 'login',
            'password': get_password()
        }).json()

        access_token = data['access_token']
        print("OK")
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        def url(path):
            return BASE.format(ip, '/nfregex' + path)

        add_service_url = url('/services/add')
        add_rule_url = url('/regexes/add')

        def start_url(service_id):
            return url(f'/service/{service_id}/start')

        for c in challenges:
            port = challenges[c]['port']
            print_fixed_width(f"Creating service {c} on port {port} ...")
            data = r.post(add_service_url, json={
                'ip_int': ip,
                'name': c,
                'port': port,
                'proto': 'tcp'
            }, headers=headers).json()

            service_id = data['service_id']
            print("OK")
            print_fixed_width(f"Starting service {c} ...")
            r.get(start_url(service_id), headers=headers)
            print("OK")

            print_fixed_width(f"Adding default rules to service {c} ...")

            for rul in rules:
                if rul.get('regex', None):
                    r.post(add_rule_url, json=rul | {
                        'service_id': service_id,
                        'active': True
                    }, headers=headers)

            print("OK")

        print("All done")

    except Exception as e:
        print("FAILED")
        print('There was a problem starting Firegex ...')
        print(e)
        stop_firegex()


setup()
