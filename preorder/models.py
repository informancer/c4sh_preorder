from django.db import models
from django.contrib.auth.models import User
from c4sh.preorder.models import PreorderTicket, PreorderPosition, Preorder
from django.db.models import Q
from django.conf import settings
import datetime
from settings import EVENT_CC_PAYMENT_API_KEY

class GoldenToken(models.Model):
	token = models.CharField(max_length=50, null=False, blank=False, verbose_name="Token", unique=True)
	ticket = models.ForeignKey('PreorderTicket', verbose_name="Ticket type")
	redeemer = models.ForeignKey(User, verbose_name="Redeemer (person who redeemed the token)", blank=True, null=True) #hoehoe, redeemer. :3
	redeemed = models.BooleanField(default=False,verbose_name="Has been redeemed yet?")
	redeem_timestamp = models.DateTimeField(null=True, blank=True, verbose_name="Redeemed on")

	def __unicode__(self):
		return "%s: %s (Redeemed: %s)" % (self.ticket.name, self.token, str(self.redeemed))

class PreorderQuota(models.Model):
	ticket = models.ForeignKey('CustomPreorderTicket', verbose_name="Ticket type")
	positions = models.ManyToManyField('PreorderPosition', null=True, blank=True, verbose_name="Positions preordered from this quota")
	quota = models.IntegerField(verbose_name="Ticket quota")
	sold = models.IntegerField(null=True, blank=True, verbose_name="Tickets preordered from this quota", default=0)

	# TODO: check if quota is available 
	#def save(self):

	def __unicode__(self):
		return "%s (%d/%d)" % (self.ticket, self.sold, self.quota)

	def recalc_quota(self):
		tickets_sold = self.positions.objects.all().count()
		self.sold = tickets_sold
		self.save()

	def get_available(self):
		return (self.quota - self.sold)


class CustomPreorderTicket(PreorderTicket):
	sortorder = models.IntegerField()
	
	class Meta:
		ordering = ['sortorder']	
	
	def stats_preordered(self):
		return CustomPreorder.objects.filter(Q(preorderposition__ticket=self)).count()

	def stats_paid(self):
		return CustomPreorder.objects.filter(Q(preorderposition__ticket=self), Q(paid=True)).count()

	def stats_paid_percentage(self):
		if self.stats_preordered() > 0:
			return float(self.stats_paid()) / float(self.stats_preordered()) * 100
		else:
			return 0

	def stats_percentage(self):
		return float(self.stats_preordered()) / float(PreorderPosition.objects.all().count()) * 100

class Tshirt(CustomPreorderTicket):
	size = models.CharField(verbose_name="T-Shirt Size", max_length=10)
	type = models.CharField(verbose_name="T-Shirt Type (girly, etc.)", max_length=255)

class PreorderPosition(PreorderPosition):
	pass

class CustomPreorder(Preorder):

	transaction_id = models.CharField(max_length=255, null=True, blank=True)

	def __unicode__(self):
		return self.unique_secret[:10]+"..."

	def get_user(self):
		return User.objects.get(pk=self.user_id)

	def get_reference_hash(self):
		return self.unique_secret[:10]		

	def payment_required_until(self):
		return self.time + datetime.timedelta(days=int(settings.EVENT_PAYMENT_REQUIRED_TIME)) # returns timedelta

	def get_sale_amount(self):
		totals_raw = {}
		try:
			tickets = self.get_tickets()
			for t in tickets:
				amount = float(t['t'].price)*int(t['amount'])
				taxes = float(amount) - (float(amount) / (float(t['t'].tax_rate)/float(100)+float(1)))

				try:
					totals_raw[t['t'].currency]['amount']+=amount
				except KeyError:
					totals_raw[t['t'].currency] = {}
					totals_raw[t['t'].currency]['amount']=amount

				try:
					[item for item in totals_raw[t['t'].currency]['taxes'] if item['rate'] == t['t'].tax_rate][0]['amount']+=taxes
				except KeyError:
					totals_raw[t['t'].currency]['taxes'] = []
					totals_raw[t['t'].currency]['taxes'].append({'rate':t['t'].tax_rate, 'amount': taxes})
				except IndexError:
					totals_raw[t['t'].currency]['taxes'].append({'rate':t['t'].tax_rate, 'amount': taxes})

			totals = []
			for t in totals_raw:
				totals.append({'currency': t, 'total': totals_raw[t]['amount'], 'taxes': totals_raw[t]['taxes']})
		except:
			raise

		return totals

	def get_positions(self):
		return PreorderPosition.objects.filter(preorder=self)

	def get_cc_transaction_status(self):
		if self.transaction_id == "":
			return False

		import pymill
		p = pymill.Pymill(EVENT_CC_PAYMENT_API_KEY)
		return p.gettrandetails(self.transaction_id)

	def get_tickets(self):
		tickets = []
		tickets_raw = []
		tickets_amount = {}
		try:
			positions = PreorderPosition.objects.filter(preorder=self)
			for p in positions:
				try:
					amount = tickets_amount[p.ticket.backend_id]
				except KeyError:
					amount = 0
				tickets_amount[p.ticket.backend_id] = amount+1

				if p.ticket not in tickets_raw:
					tickets_raw.append(p.ticket)
		except:
			raise

		for ticket in tickets_raw:
			tickets.append({'t':ticket, 'amount':tickets_amount[ticket.backend_id]})

		return tickets

