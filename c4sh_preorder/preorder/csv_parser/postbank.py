import re
import datetime
from decimal import Decimal, getcontext, ROUND_HALF_UP
import settings
from . import Status

def parse_row(row):
	if len(row) is not 8 or str(row[0]) == str("Buchungstag"):
		return False

	# row[0] is Buchungstag
	# row[1] is Wertstellung
	# row[2] is Umsatzart
	# row[3] is Buchungsdetails (!)
	# row[4] is Auftraggeber
	# row[5] is Empfaenger
	# row[6] is Betrag
	# row[7] is Saldo

	date = datetime.datetime.strptime(row[0], "%d.%m.%Y")

	getcontext().prec = 20 # set Decimal precision to 20

	row[6] = re.sub(' \\x80', '', row[6]) # replacing malicious EUR symbol
	row[6] = re.sub('\.', '', row[6]) # remove Tausendertrennzeichen (fixes #29)
	row[6] = re.sub(',', '.', row[6]) # replacing , with . for float formatting
	row[6] = Decimal(row[6]).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


	# sometimes people/banks mix up - and whitespaces. Regex to the rescue!
	reference_hash = re.compile('%s[-\ ]?[a-fA-F0-9]{10}' % settings.EVENT_PAYMENT_PREFIX,re.IGNORECASE).findall(row[3])

	#lets check if someone managed to put the reference more than once into the payment
	#if we can reduce the set -> put it into the match procedure
	# if not, put it into the unmatched list

	if len(reference_hash) != len(set(reference_hash)):
		reference_hash = list(set(reference_hash))

	# trying to figure out if some brains are unable to use the right reference code
	if not reference_hash:
		reference_hash = re.compile('[a-fA-F0-9]{10}').findall(row[3])

	# try removing all whitespace to get a result. lots of banks add whitespace.
	if not reference_hash:
		tmp = re.sub('\s', '', row[3])
		reference_hash = re.compile('[a-fA-F0-9]{10}').findall(tmp)

	# okay, giving up
	if not reference_hash:
		reference_hash = []
		reference_hash.append(row[3])

	if len(reference_hash) == 1:
		reference_hash_only = re.compile('[a-fA-F0-9]{10}').findall(reference_hash[0])

	if len(reference_hash_only) == 1:
		return (Status.Success, date, row[4], row[3], reference_hash_only[0], row[6])
	else:
		return (Status.Failure, date or row[0], row[4], row[3], None, row[6])
