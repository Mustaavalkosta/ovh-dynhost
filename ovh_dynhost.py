#! /usr/bin/env python3
"""
A simple script to update the OVH DynHost entry with the current external IP of this machine.
"""

import argparse
import configparser
import datetime
import ipgetter
import requests
import socket
import sys

def main():
	ap = argparse.ArgumentParser(prog='ovh_dynhost', description='Updates the OVH DynHost entry to the current IP address.')
	ap.add_argument('-c', '--config', help='The configuration file location.')
	args = ap.parse_args()

	if args.config:
		config_file = args.config
	else:
		config_file = 'config.ini'

	cp = configparser.ConfigParser()

	if len(cp.read(config_file)) == 0:
		loge("Config file is missing or empty.")
		sys.exit(-1)

	for section in cp.sections():
		domain = section

		if cp.has_option(section, 'Username'):
			username = cp.get(domain, 'Username')

		if cp.has_option(section, 'Password'):
			password = cp.get(domain, 'Password')

		if cp.has_option(section, 'IP'):
			ip = cp.get(domain, 'IP')
		else:
			ip = ipgetter.myip()

		if not check_dns(domain, ip):
			update_dns(domain, ip, username, password)
		else:
			logi(domain + ": IP did not change.")

def check_dns(domain, ip):
	addr_info = socket.getaddrinfo(domain, 80)
	for i in range(len(addr_info)):
		if addr_info[i][4][0] == ip:
			return True
		
	return False

def update_dns(domain, ip, username, password):
	queryArguments = {'system':'dyndns', 'hostname':domain, 'myip':ip}
	response = requests.get("https://www.ovh.com/nic/update", params=queryArguments, auth=(username, password))
	if response.text.startswith('good ' + ip):
			logi("Update to " + ip + " successful.")
			sys.exit(0)
	elif response.text.startswith('nochg ' + ip):
			logi("Update failed. IP did not change.")
			sys.exit(0)
	elif response.status_code == requests.codes.get(401):
		# 401 Authentification failed
		loge("Authentification failed. Username or password is wrong.")
		sys.exit(-2)
	elif response.status_code == requests.codes.get(403):
		# 403 Forbidden
		loge("Authentification is missing.")
		sys.exit(-3)
	
	loge("Update failed. (" + response.text + ")")
	sys.exit(-1)

def get_date():
	return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

def logi(str):
	sys.stdout.write("[" + get_date() + "] " + str + "\n")

def loge(str):
	sys.stderr.write("[" + get_date() + "] " + str + "\n")

if __name__ == '__main__':
	main()
