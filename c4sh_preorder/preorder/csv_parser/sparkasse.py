# encoding: utf-8
import re
import datetime
from decimal import Decimal, getcontext, ROUND_HALF_UP
import settings
from . import Status

def parse_row(row):
	if len(row) < 8 or str(row[0]) == str("Kontonummer"):
		return False

	# row[0] is Kontonummer
	# row[1] is Datum
	# row[2] is Datum Wertstellung
	# row[3] is Geschaeftsvorfall (e.g. "Lastschrift", "Überweisungsgutschrift")
	# row[4] is Verwendungszweck
	# row[5] is Betrag
	# row[6] is Currency (check this to be "EUR", fail otherwise)
	# row[7] is Auftraggeber
	# row[8] is Konto (most likely empty)
	# row[9] is BLZ (most likely empty)

	date = datetime.datetime.strptime(row[1], "%d.%m.%Y")

	getcontext().prec = 20 # set Decimal precision to 20

	# make sure the currency is correct
	if row[6] != "EUR":
		# i'll just set the amount to zero, so it'll fail
		row[5] = "0,00"

	# clean up the amount
	row[5] = re.sub('\.', '', row[5]) # remove Tausendertrennzeichen
	row[5] = re.sub(',', '.', row[5]) # replacing , with . for decimal formatting
	row[5] = Decimal(row[5]).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

	# sometimes people/banks mix up - and whitespaces. Regex to the rescue!
	reference_hash = re.compile('%s[-\ ]?[a-fA-F0-9]{10}' % settings.EVENT_PAYMENT_PREFIX,re.IGNORECASE).findall(row[4])

	#lets check if someone managed to put the reference more than once into the payment
	#if we can reduce the set -> put it into the match procedure
	# if not, put it into the unmatched list

	if len(reference_hash) != len(set(reference_hash)):
		reference_hash = list(set(reference_hash))

	# trying to figure out if some brains are unable to use the right reference code
	if not reference_hash:
		reference_hash = re.compile('[a-fA-F0-9]{10}').findall(row[4])

	# try removing all whitespace to get a result. lots of banks add whitespace.
	if not reference_hash:
		tmp = re.sub('\s', '', row[4])
		reference_hash = re.compile('[a-fA-F0-9]{10}').findall(tmp)

	# okay, giving up
	if not reference_hash:
		reference_hash = []
		reference_hash.append(row[4])

	reference_hash_only = ""
	if len(reference_hash) == 1:
		reference_hash_only = re.compile('[a-fA-F0-9]{10}').findall(reference_hash[0])

	if len(reference_hash_only) == 1:
		return (Status.Success, date, row[7], row[4], reference_hash_only[0], row[5])
	else:
		return (Status.Failure, date or row[1], row[7], row[4], None, row[5])
