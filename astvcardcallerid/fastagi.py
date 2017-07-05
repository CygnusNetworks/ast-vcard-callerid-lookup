#!/usr/bin/env python
# coding=utf-8

import argparse
import logging
import os
import SocketServer
import sys

import asterisk.agi
import phonenumbers

from . import config
from . import vcard_parser
from . import __version__

log = logging.getLogger("astvcardcallerid")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
log.addHandler(ch)


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
		log.debug("Received FastAGI request for client %s:%s", self.client_address[0], self.client_address[1])
		try:
			devnull = open(os.devnull, 'w')
			agi = asterisk.agi.AGI(self.rfile, self.wfile, devnull)
			num = agi.get_variable('CALLERID(num)')
			log.debug("FastAGI request for client %s:%s for number %s", self.client_address[0], self.client_address[1], num)
			parsed_num = phonenumbers.parse(num, self.server.config["general"]["origin"])
			e164 = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164)
			log.debug("FastAGI request for client %s:%s for E164 number %s", self.client_address[0], self.client_address[1], e164)
			numbers = self.server.contact_data.keys()
			text = None
			if e164 in numbers:
				text = self.make_text(self.server.contact_data[e164])
				log.debug("FastAGI request for client %s:%s for E164 number %s results in Caller ID %s", self.client_address[0], self.client_address[1], e164, text)
			else:
				for number in numbers:
					if number.endswith("0") and "org" in self.server.contact_data[number]:
						if e164[:len(number) - 2] == number[:-1]:
							text = self.make_text(self.server.contact_data[number])
							break
				log.debug("FastAGI request for client %s:%s for E164 number %s results in Organiztion Caller ID %s", self.client_address[0], self.client_address[1], e164, text)

			if text is not None:
				agi.set_variable("CALLERID_VCARD", text)
			if e164 in numbers:
				if "org" in self.server.contact_data[e164]:
					agi.set_variable("CALLERID_VCARD_ORG", self.server.contact_data[e164]["org"])
				if "fn" in self.server.contact_data[e164]:
					agi.set_variable("CALLERID_VCARD_FULLNAME", self.server.contact_data[e164]["fn"])
		except Exception as e:
			print(e)
		finally:
			devnull.close()


def main():
	argp = argparse.ArgumentParser()
	argp.add_argument("-d", "--directory", help="Set directory for vcards", default=None)
	argp.add_argument("-i", "--ip", help="Set bind ip for FastAGI", default=None)
	argp.add_argument("-p", "--port", help="Set bind port for FastAGI", type=int, default=None)

	args = argp.parse_args()  # pylint: disable=W0612

	conf = config.ASTVCardCallerIDConfig()
	c = conf.get_configobj()

	if args.directory is not None:
		vcard_dir = args.directory
	else:
		vcard_dir = c["general"]["vcard_dir"]

	if args.ip is not None:
		ip = args.ip
	else:
		ip = c["general"]["ip"]

	if args.port is not None:
		port = args.port
	else:
		port = c["general"]["port"]

	SocketServer.TCPServer.allow_reuse_address = True
	server = SocketServer.TCPServer((ip, port), ASTVCardCallerID)
	log.info("astvcardcallerid version %s starting", __version__)
	log.debug("Start parsing contacts from dir %s", vcard_dir)
	cards = vcard_parser.read_cards(vcard_dir)
	server.contact_data = vcard_parser.parse_cards(cards)
	num_numbers = len(server.contact_data.keys())
	if num_numbers == 0:
		log.error("No numbers found. Not serving any callerids")
		sys.exit(0)
	log.debug("Finished parsing contact data - Found %i distinct numbers", num_numbers)
	server.config = c
	try:
		log.debug("Server FastAGI on %s:%s", ip, port)
		server.serve_forever()
	except KeyboardInterrupt as e:
		log.info("Shutdown on ctrl-c")
		sys.exit(0)
	except Exception as e:
		log.exception("Unknown Exception %s occured", e)
		sys.exit(1)

if __name__ == "__main__":
	main()
