# coding=utf-8
import logging
import os
import phonenumbers
import re
import vobject


log = logging.getLogger("astvcardcallerid.vcard_parser")

def read_cards(directory):
	cards = []
	files = os.listdir(directory)
	files.sort()
	for filename in files:
		if os.path.isfile(os.path.join(directory, filename)) and filename.endswith(".vcf"):
			with open(os.path.join(directory, filename), 'r') as f:
				log.debug("Parsing vcard filename %s", filename)
				data = f.readlines()
			for line in data:
				if re.match(r"^BEGIN:VCARD", line):
					newcard = line
				elif re.match(r"^END:VCARD", line):
					newcard += line
					cards.append(vobject.readOne(newcard.decode('utf-8')))
				else:
					newcard += line
	return cards


def parse_cards(cards, origin="DE"):
	numbers = dict()
	for card in cards:
		if "tel" in card.contents:
			for tel in card.contents['tel']:
				t = num = org = None
				if hasattr(tel, "type_param"):
					t = tel.type_param
				fn = card.fn.value
				if hasattr(card, "org"):
					org = card.org.value[0]
				# strip all GSM phone number specials like dial *31# or #31#
				num_pre = re.sub(r'^(\*|\#).*\#', '', tel.value)
				# Remove everything non digit or +
				num_pre = re.sub(r'[^0-9+]', '', num_pre)
				try:
					if num_pre is not None and len(num_pre) > 3:
						if num_pre.startswith("+"):
							num = phonenumbers.parse(num_pre.decode('utf-8'))
						else:
							num = phonenumbers.parse(num_pre.decode('utf-8'), origin)
					else:
						continue
				except UnicodeDecodeError:
					pass
				if num is not None and t is not None and phonenumbers.is_valid_number(num):
					e164 = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
					if e164 not in numbers:
						numbers[e164] = dict(fn=fn, card=card)
					if t is not None:
						numbers[e164]["type"] = t
					if org is not None:
						numbers[e164]["org"] = org

	return numbers
