import urllib
from settings import *

def make_bezahlcode_uri(reference, amount):
	reason = "%s-%s" % (EVENT_PAYMENT_PREFIX, reference)
	amount = str(amount).replace(".",",")
	uri = "bank://singlepaymentsepa?name=%s&iban=%s&bic=%s&reason=%s&amount=%s" % \
			(urllib.quote_plus(EVENT_BEZAHLCODE_NAME), \
				urllib.quote_plus(EVENT_BEZAHLCODE_IBAN), \
				urllib.quote_plus(EVENT_BEZAHLCODE_BIC), \
				urllib.quote_plus(reason), \
				urllib.quote_plus(amount))

	return uri
