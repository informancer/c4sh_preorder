#!/home/www/presale/presale/bin/python

import settings
from django.core.management import setup_environ
setup_environ(settings)
import time, sys, uuid
from django.db import transaction
from c4sh_preorder.preorder.models import *

guest = CustomPreorderTicket.objects.get(name="Gast-Ticket")
speaker = CustomPreorderTicket.objects.get(name="Speakerticket")
press = CustomPreorderTicket.objects.get(name="Presseticket")
booth = CustomPreorderTicket.objects.get(name="Standbetreiber-Ticket")

argvmap = {'gast': guest,
           'speaker': speaker,
           'presse': press,
           'booth': booth,
           'stand': booth}

try:
	ticket = argvmap[sys.argv[1]]
	ticket.pk
	assert int(sys.argv[2]) > 0
except:
	print "%s (%s) count" % (sys.argv[0], "|".join(argvmap.keys()))
	sys.exit(0)

@transaction.commit_on_success
def generate():
	for i in range(0, int(sys.argv[2])):
		g = GoldenToken(token=uuid.uuid4(), ticket=ticket)
		g.save()
		print g.token

if __name__ == "__main__":
	generate()
