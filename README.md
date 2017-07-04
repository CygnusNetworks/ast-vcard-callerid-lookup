# Asterisk VCard Caller ID Lookup

This small Asterisk FastAGI script written in Python provides a caller ID lookup based on VCard (VCF) Addressbook contact exports for the Asterisk PBX. On incoming calls the incoming number is matched against all entries of all found VCards in a specific directory and extracts the Full name of the corresponding addressbook entry. In addition it is possible to extract the company/organization and also the type of the contact number (home, work, cellphone, iphone).

Phone numbers are matched, validated and normalized agains the Google Phonenumber Library. If no match is found, shorter phonenumbers ending with 0 are matched for Company/Organization records.
Lets say you have a Company/Organization Something with some phone number ...47110 in your vCards and have some caller calling with ...471129 it will match this against the company phone number, if no contact for ...471129 is present.
This might only be useful in countries with non fixed number lengths.
The resulting text is set to the Asterisk variable CALLERID_VCARD.

## Dependencies

 - Python 2.7 Interpreter
 
 Python Modules:
 
 - Configobj
 - vobject
 - phonenumbers
 
## Installation

Installation can be done using:

```
python setup.py install
```

Drop your vCards or vCards lists (macOS Adressbook Export of multiple contacts) into /usr/share/astvcardcallerid.

Afterwards you can start the FastAGI Prozess using:

```
/usr/bin/astvcardcallerid
```

It will listen on localhost ip 127.0.0.1:4573 for incoming TCP FastAGI connections.

In Asterisk you can define a macro in the following way and set for example the CALLERID(name) variable:

```
[macro-vcard-callerid]
exten => s,1,Noop(Received caller ID request for callerid ${CALLERID(all)})
same => n,AGI(agi://127.0.0.1:4573)
same => n,Noop(Caller ID lookup resulted in ${CALLERID_VCARD})
same => n,Set(CALLERID(name)=${CALLERID_VCARD})
```

To use this macro on inbound calls in the following way:

```
[from-pstn]
exten => _X,1,Noop(Incoming call to from caller id ${CALLERID(num)})
same => n,Noop(Executing callerid macro)
same => n,Macro(vcard-callerid)
same => n,Noop(Incoming call to from caller id ${CALLERID(num)} and name ${CALLERID(name)})
```

The FastAGI script is intended to be started as a SystemD (simple) service. A service file is found in the repository and can provide startup on system start:

```
sudo cp astvcardcallerid.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable astvcardcallerid
sudo systemctl start astvcardcallerid
```

A RPM spec file is provided and tested on RHEL 7 / CentOS 7.

## Configuration

Behaviour can be changed using a configfile in /etc/astvcardcallerid.conf. A example file is given below including the default values:

```
[general]
ip = 127.0.0.1
port = 4573
origin = DE
vcard_dir = /usr/share/astvcardcallerid
add_type = True
add_org = True
```

IP/Port can be changed by configuring ip/port. The Origin is used on incoming calls to match numbers against a country specific dialplan (Default is DE for Germany). In addition the Origin field is used on phone numbers in vCards not having international prefixes (+...).
The add_type option will add [C], [H], [W] after the full name of the identified caller to reflect Cell, Home or Work phonenumber. In addition add_org will extract Company/Organization and add this after the contact full name. 
