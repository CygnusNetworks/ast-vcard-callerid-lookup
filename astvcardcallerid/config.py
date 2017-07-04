# coding=utf-8

import configobj
import validate

CONFIG_SPEC_SOURCE = """
[general]
ip = string(default="127.0.0.1")
port = integer(min=1024,max=65535,default=4573)
origin = string(min=2,max=2,default="DE")
vcard_dir = string(default="/usr/share/astvcardcallerid")
add_type = boolean(default=True)
add_org = boolean(default=True)
"""


class ASTVCardCallerIDConfig(object):
	def __init__(self, configfile="/etc/astvcardcallerid.conf"):
		config_spec_parsed = configobj.ConfigObj(CONFIG_SPEC_SOURCE.format().splitlines(), list_values=False)

		self.config = configobj.ConfigObj(configfile, file_error=False, configspec=config_spec_parsed)
		validator = validate.Validator()
		res = self.config.validate(validator, preserve_errors=True)
		for section_list, key, error in configobj.flatten_errors(self.config, res):  # pylint: disable=W0612
			raise RuntimeError("Failed to validate section %s key %s in config file %s" % (", ".join(section_list), key, configfile))

	def get_configobj(self):
		"""Function returning created ConfigObj

		:return: ConfigObj
		:rtype: class
		"""
		return self.config
