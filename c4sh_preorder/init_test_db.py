import datetime
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from preorder.models import *

def date(pd):
	return datetime.datetime.strptime(pd, "%Y-%m-%dT%H:%M:%SZ")

t1 = CustomPreorderTicket(
	name = "Dauerkarte",
	backend_id = 1,
	price = 28.53,
	currency = "EUR",
	tax_rate = 19,
	limit_timespan = False,
	limit_amount = 9000,
	limit_amount_user = 5,
	is_ticket = True,
	sortorder = 10,
	active = True
	)
t1.save()

t2 = Tshirt(
	name = "T-Shirt Girly M",
	backend_id = 2,
	price = 15.00,
	currency = "EUR",
	tax_rate = 19,
	limit_timespan = False,
	limit_amount = 20,
	limit_amount_user = 2,
	is_ticket = True,
	sortorder = 20,
	size = "M",
	type = "girly",
	active = True
	)
t2.save()

q1 = PreorderQuota(
	ticket = t1,
	quota = 200
	).save()

q2 = PreorderQuota(
	ticket = t2,
	quota = 10
	).save()
