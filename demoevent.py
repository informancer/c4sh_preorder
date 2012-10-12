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

# Short name of your event
EVENT_NAME_SHORT = 'SIGINT12'

# Unix-friendly name of your event (lowercase, a-z0-9)
EVENT_NAME_UNIX = 'sigint12'

# Official name of your event
EVENT_NAME = 'SIGINT12'

#Official logo for your event, located inside STATIC_ROOT. Will be used for PDF output of tickets and stuff
EVENT_LOGO = 'sigint12.png'


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
EVENT_PAYMENT_PREFIX = "SIGINT12"

# Description for CC paments
EVENT_CC_PAYMENT_DESC = "SIGINT12"

# API key for CC payments
EVENT_CC_PAYMENT_API_KEY = ""

# Bank details for payment
EVENT_PAYMENT_DETAILS =  "Chaos Computer Club Ossendorf ltd.\n" + \
 "Institut: Ehrenfelder Bank AG\n" + \
 "BLZ: 10000000\n" + \
 "Kto: 1\n" + \
 "IBAN: DEFoo\n" + \
 "SWIFT/BIC: Bar"

# Supervisor information
EVENT_DASHBOARD_TEXT = "Here be important event-related supervisor information.<br />" + \
                       "You can define this text in EVENT_DASHBOARD_TEXT."
# Event description
EVENT_DESCRIPTION_TEXT = "Die SIGINT ist eine dreit&auml;gige Konferenz des CCC Ossendorf in K&ouml;ln, die sich mit Techniken wie Bluetooth hacking, EFI rootkits und Malware Analysis on Android Phones, aber auch um gesellschaftspolitische Forderungen und Utopien, um Hacktivismus, kreative Normverletzungen und Premium-Erfas befasst.\n"

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
EVENT_FOOTER_NOTE = "Bei Fragen und Problemen bitte direkt eine Mail an die <a href='mailto:"+EVENT_CONTACT_MAILTO+"'>SIGINT Orga Crew</a>"

# do not allow downloads before this date, YYYY-mm-dd HH:MM:SS
EVENT_DOWNLOAD_DATE = "2012-09-28 00:00:00"

# Supervisor IPs
EVENT_SUPERVISOR_IPS = ('127.0.0.1', '172.17.0.1',)
