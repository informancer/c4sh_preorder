import datetime
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from preorder.models import *

def date(pd):
	return datetime.datetime.strptime(pd, "%Y-%m-%dT%H:%M:%SZ")

t1 = CustomPreorderTicket(
	name = "Standard",
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

q1 = PreorderQuota(
	ticket = t1,
	quota = 200
	).save()

t1 = CustomPreorderTicket(
	name = "Supporter",
	backend_id = 1,
	price = 128.53,
	currency = "EUR",
	tax_rate = 19,
	limit_timespan = False,
	limit_amount = 9000,
	limit_amount_user = 5,
	is_ticket = True,
	sortorder = 20,
	active = True
	)
t1.save()

q1 = PreorderQuota(
	ticket = t1,
	quota = 200
	).save()

t1 = CustomPreorderTicket(
	name = "Business",
	backend_id = 1,
	price = 228.53,
	currency = "EUR",
	tax_rate = 19,
	limit_timespan = False,
	limit_amount = 9000,
	limit_amount_user = 5,
	is_ticket = True,
	sortorder = 30,
	active = True
	)
t1.save()

q1 = PreorderQuota(
	ticket = t1,
	quota = 200
	).save()

m_shirt = Merchandise(name="T-Shirt", detail_text="design coming soon", active=True)
m_shirt.save()
m_hoodie = Merchandise(name="Hoodie", detail_url="https://events.ccc.de/", detail_text="foobar", active=True)
m_hoodie.save()

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
	sortorder = 40,
	size = "M",
	type = "girly",
	merchandise = m_shirt,
	active = True
	)
t2.save()

i = 0
for size in ['S', 'M', 'L', 'XL', 'XXL', '3XL']:
	t3 = Tshirt(
		name = "T-Shirt %s" % size,
		backend_id = 200+i,
		price = 15.00,
		currency = "EUR",
		tax_rate = 19,
		limit_timespan = False,
		limit_amount = 20,
		limit_amount_user = 2,
		is_ticket = True,
		sortorder = 50+i,
		size = size,
		type = "regular",
		merchandise = m_shirt,
		active = True
		)
	t3.save()
	i += 1
	q3 = PreorderQuota(
		ticket = t3,
		quota = 200
	).save()

for size in ['S', 'M', 'L', 'XL', 'XXL']:
	t3 = Tshirt(
		name = "Hoodie %s" % size,
		backend_id = 200+i,
		price = 30.00,
		currency = "EUR",
		tax_rate = 19,
		limit_timespan = False,
		limit_amount = 20,
		limit_amount_user = 2,
		is_ticket = True,
		sortorder = 50+i,
		size = size,
		type = "regular",
		merchandise = m_hoodie,
		active = True
		)
	t3.save()
	i += 1
	q3 = PreorderQuota(
		ticket = t3,
		quota = 200
	).save()

q2 = PreorderQuota(
	ticket = t2,
	quota = 10
	).save()
