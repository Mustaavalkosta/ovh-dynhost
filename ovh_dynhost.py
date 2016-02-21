#! /usr/bin/env python3
"""
A simple script to update the OVH DynHost entry with the current external IP of this machine.
"""

import configparser
import ipgetter
import requests
import socket
import sys

def main():
	cp = configparser.ConfigParser()
	if len(cp.read('config.ini')) == 0:
		sys.stderr.write("Config file is missing or empty.\n")
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
			sys.stdout.write(domain + ": IP did not change.\n")

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
			sys.stdout.write("Update to " + ip + " successful.\n")
			sys.exit(0)
	elif response.status_code == requests.codes.get(401):
		# 401 Authentification failed
		sys.stderr.write("Authentification failed. Username or password is wrong.\n")
		sys.exit(-2)
	elif response.status_code == requests.codes.get(403):
		# 403 Forbidden
		sys.stderr.write("Authentification is missing.\n")
		sys.exit(-3)
	
	sys.stderr.write("Update failed.\n")
	sys.exit(-1)

if __name__ == '__main__':
	main()
