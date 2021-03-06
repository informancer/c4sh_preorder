# -*- coding: utf-8 -*-
"""
c4sh_preorder event config
=================

You'll create one of these files per event. It contains certain
constants used by the software for this event. c4sh_preorder can only have
one event loaded at a time.
When you change this file in production, remember to restart all
python processes or else the changes won't be in effect.
"""

# Allowed HTTP Hostnames of your presale installation
ALLOWED_HOSTS = [
    'presale.events.ccc.de',
]

# Short name of your event
EVENT_NAME_SHORT = '30C3'

# Unix-friendly name of your event (lowercase, a-z0-9)
EVENT_NAME_UNIX = '30c3'

# Official name of your event
EVENT_NAME = '30th Chaos Communication Congress'

#Official logo for your event, located inside STATIC_ROOT. Will be used for PDF output of tickets and stuff
EVENT_LOGO = '30c3.png'


# Postal address of host (for invoices)
EVENT_INVOICE_ADDRESS = "Chaos Computer Club\nVeranstaltungsgesellschaft mbH\n" + \
 "Postfach 31337\n" + \
 "50666 Ossendorf\n"

# Legal information (for invoices)
EVENT_INVOICE_LEGAL = "AG Ossendorf HRB 31337\nUSt-ID: DE9000"

# Time and location of your event (for invoices)
EVENT_TIME_AND_LOCATION = "18.05.-20.05.12, Ossendorf"

# Your name (yes, your name. You, the one setting up this software!)
EVENT_C4SH_SUPPORT_CONTACT = "You <your@mail>"

# Max. time between preorder and payment (in days, int)
EVENT_PAYMENT_REQUIRED_TIME = 14

# Max. tickets to be sold (= venue sold out)
EVENT_VENUE_PAYLOAD = 3000

# mailto: for contact menu entry
EVENT_CONTACT_MAILTO = "orga@tld"

# Prefix for bank transfer references
EVENT_PAYMENT_PREFIX = "30C3"

# Bank details for payment
EVENT_PAYMENT_DETAILS =  "Chaos Computer Club Ossendorf ltd.\n" + \
 "Bank: Ehrenfelder Bank AG\n" + \
 "BLZ: 10000000\n" + \
 "Kto: 1234567890\n" + \
 "IBAN: DE23100000001234567890\n" + \
 "SWIFT/BIC: DEH3RPD"

# Bezahlcode integration, see http://bezahlcode.de for more information
EVENT_BEZAHLCODE_ENABLE = False
EVENT_BEZAHLCODE_NAME = "CCCO ltd."
EVENT_BEZAHLCODE_IBAN = "DE00000000000000000000000" # No spaces
EVENT_BEZAHLCODE_BIC = "COKSDE33" # No spaces

# Supervisor information
EVENT_DASHBOARD_TEXT = "Here be important event-related supervisor information.<br />" + \
                       "You can define this text in EVENT_DASHBOARD_TEXT."
# Event description
EVENT_DESCRIPTION_TEXT = "December 27<sup>th</sup>-30<sup>th</sup>, 2013 – Hamburg, Germany\n"

# Additional information about tickets, to be shown below the ticket selection
EVENT_TICKET_INFO = "Hackers under the age of 18 years qualify for the <em>Up-and-coming</em> ticket. Hackers under the age of 12 years get in for free while accompanied by an adult."

# Text for payment ack notification email
EVENT_PAYMENT_ACK_MAIL_TEXT = 	"English version below" + \
 "\n------------------------------- " + \
 "\n\nHallo," + \
 "\nwir haben Deine Zahlung erhalten. Der Ticket-Download wird allerdings erst  einige Tage vor der Konferenz freigeschaltet." + \
 "\nWir informieren Dich via E-Mail, sobald das Ticket zum Download bereit steht." + \
 "\nSolltest Du noch Fragen haben, kannst Du uns unter "+EVENT_CONTACT_MAILTO+" erreichen." + \
 "\n\nBis zur SIGINT12!\nSIGINT-Orga" + \
 "\n\n--" + \
 "\n\nHi," + \
 "\nwe have successfully received your payment. Your ticket will be ready for download a few days before the conference starts. " + \
 "\nWe will send you another mail as soon as your ticket is ready." + \
 "\nIf you have any questions, do not hesitate to contact us at "+EVENT_CONTACT_MAILTO+"." + \
 "\n\nSee you on SIGINT12!\nSIGINT Orga"

# Footer note visible on all pages
EVENT_FOOTER_NOTE = "If you experience any difficulties with our presale, please contact the <a href='mailto:"+EVENT_CONTACT_MAILTO+"'>30C3 Orga</a>."

# do not allow downloads before this date, YYYY-mm-dd HH:MM:SS
EVENT_DOWNLOAD_DATE = "2012-09-28 00:00:00"

# Supervisor IPs
EVENT_SUPERVISOR_IPS = ('127.0.0.1', '172.17.0.1',)

# Minimum amount required to require a billing address
EVENT_BILLING_ADDRESS_LIMIT = 150.00

# CSV parser module (see backend/csv_parser/*.py)
EVENT_CSV_PARSER = "sparkasse"
EVENT_CSV_DELIMITER = "\t"

#Enables CC payment options when set to True
EVENT_CC_ENABLE = False

# When using Credit Card payments, configure fees here
EVENT_CC_FEE_PERCENTAGE = 7.5 # 7.5% of the sale amount
EVENT_CC_FEE_FIXED = 7.5 # 7.50 EUR per transaction
# We'd then deduct $fee + 7.5 EUR * 1.075

# DaaS settings
# this is required for invoice generation and currently
# not available under our open source license. please
# contact zakx@koeln.ccc.de if you're interested.
EVENT_DAAS_ENABLE = True
EVENT_DAAS_API_BASE = "http://192.168.50.3:8001"
EVENT_DAAS_API_ENDPOINT = "/api/v1/"
EVENT_DAAS_FEATURES = [
	"invoice",
]
EVENT_DAAS_INVOICE_NUMBER_FORMAT = "30C3-VVK-%(invoice_id)06d"

# Passbook settings

# Enables Passbook download when set to True
EVENT_PASSBOOK_ENABLE = False

EVENT_PASSBOOK_FROM = "July 5th, 2013" # Event from date, e.g. "27th December"
EVENT_PASSBOOK_TO = "July 7th, 2013"  # Event from date, e.g. "30th December"
EVENT_PASSBOOK_ORGANISATION = "SIGINT 2013" # Organisation, shown on lockscreen
EVENT_PASSBOOK_IDENTIFIER = "pass.de.ccc.events...." # Passbook cert identifier
EVENT_PASSBOOK_TEAMIDENTIFIER = "" # Passbook cert team identifier
EVENT_PASSBOOK_DESCRIPTION = "SIGINT13 Ticket" # Passbook ticket description
EVENT_PASSBOOK_BG_COLOR = "rgb(51,51,51)" # Passbook background color
EVENT_PASSBOOK_FG_COLOR = "rgb(255,255,255)" # Passbook foreground color
EVENT_PASSBOOK_LOGO_TEXT = "SIGINT 2013" # Passbook logo text
EVENT_PASSBOOK_FILES_PATH = "/home/vagrant/c4sh_preorder/passbook" # Absolute path to passbook files folder which contains certs and logo
EVENT_PASSBOOK_PASSWORD = "" # Passbook cert private key password
EVENT_PASSBOOK_LOCATION = (50.948463, 6.943885) # (lat, long)
EVENT_PASSBOOK_RELEVANT_DATE = "2013-07-05T10:00:00+02:00" # when passbook gets relevant, ISO 8601 like "2013-07-05T10:00:00+02:00"

"""
passbook howto:
EVENT_PASSBOOK_FILES_PATH needs to point to a directory containing the following files:
Certificates.p12
certificate.pem
key.pem
wwdr.pem

icon.png -- 114x114px
background.png -- 180x220px, gets blurred automatically
background@2x.png -- 360x440px, gets blurred automatically
logo.png -- 160x50px
logo@2x.png -- 320x100px
"""

# Friends settings
EVENT_FRIENDS_ENABLED = True # enable friends tickets applications?
EVENT_FRIENDS_TICKET_PREFIX = "Friends " # prefix of the friends tickets
EVENT_FRIENDS_EMAIL = "you@email" # email address of the application review team
