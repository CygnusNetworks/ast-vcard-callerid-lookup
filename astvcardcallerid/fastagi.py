#!/usr/bin/env python
# coding=utf-8

import SocketServer
import os
import sys

import asterisk.agi
import phonenumbers

from . import config
from . import vcard_parser


class ASTVCardCallerID(SocketServer.StreamRequestHandler, SocketServer.ThreadingMixIn, object):
	def make_text(self, contact):
		text = ""
		if "fn" in contact:
			text += contact["fn"]
		if self.server.config["general"]["add_type"] and "type" in contact:
			text += " [%s]" % contact["type"][0]
		if self.server.config["general"]["add_org"] and "org" in contact:
			if "fn" in contact:
				text += " (%s)" % contact["org"]
			else:
				text += contact["org"]
		return text

	def handle(self):
		print("Received FastAGI request for client %s:%s" % self.client_address)
		try:
			devnull = open(os.devnull, 'w')
			agi = asterisk.agi.AGI(self.rfile, self.wfile, devnull)
			num = agi.get_variable('CALLERID(num)')
			print("FastAGI request for client %s:%s for number %s" % (self.client_address[0], self.client_address[1], num))
			parsed_num = phonenumbers.parse(num, self.server.config["general"]["origin"])
			e164 = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164)
			print("FastAGI request for client %s:%s for E164 number %s" % (self.client_address[0], self.client_address[1], e164))
			numbers = self.server.contact_data.keys()
			text = None
			if e164 in numbers:
				text = self.make_text(self.server.contact_data[e164])
				print("FastAGI request for client %s:%s for E164 number %s results in Caller ID %s" % (self.client_address[0], self.client_address[1], e164, text))
			else:
				for number in numbers:
					if number.endswith("0") and "org" in self.server.contact_data[number]:
						if e164[:len(number)-2] == number[:-1]:
							text = self.make_text(self.server.contact_data[number])
							break
				print("FastAGI request for client %s:%s for E164 number %s results in Organiztion Caller ID %s" % (self.client_address[0], self.client_address[1], e164, text))

			if text is not None:
				agi.set_variable("CALLERID_VCARD", text)
		except Exception as e:
			print(e)
		finally:
			devnull.close()

def main():
	conf = config.ASTVCardCallerIDConfig()
	c = conf.get_configobj()
	SocketServer.TCPServer.allow_reuse_address = True
	server = SocketServer.TCPServer((c["general"]["ip"], c["general"]["port"]), ASTVCardCallerID)
	print("astvcardcallerid starting")
	print("Start parsing contacts")
	cards = vcard_parser.read_cards(c["general"]["vcard_dir"])
	server.contact_data = vcard_parser.parse_cards(cards)
	num_numbers = len(server.contact_data.keys())
	if num_numbers == 0:
		print("No numbers found. Not serving any callerids")
		sys.exit(0)
	print("Finished parsing contact data - Found %i distinct numbers" % num_numbers)
	server.config = c
	try:
		print("Server FastAGI on %s:%s" % (c["general"]["ip"], c["general"]["port"]))
		server.serve_forever()
	except KeyboardInterrupt as e:
		print("Shutdown on ctrl-c")
		sys.exit(0)
	except Exception as e:
		print("Unknown Exception %s occured" % e)
		sys.exit(1)

if __name__ == "__main__":
	main()