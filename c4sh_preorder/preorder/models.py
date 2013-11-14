from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from c4sh.preorder.models import PreorderTicket, PreorderPosition, Preorder
from django.db.models import Q
from django.conf import settings
import datetime

class UserProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True, related_name='user_profile')

	# Hack to avoid IntegrityErrors while using Django forms to create users
	def save(self, *args, **kwargs):
		if not self.pk:
			try:
				p = UserProfile.objects.get(user=self.user)
				self.pk = p.pk
			except UserProfile.DoesNotExist:
				pass
		super(UserProfile, self).save(*args, **kwargs)

	@property
	def has_preorders(self):
		return (CustomPreorder.objects.filter(user_id=self.user.pk).count() >= 1)

	def get_preorders(self):
		try:
			return CustomPreorder.objects.filter(user_id=request.user.pk)
		except CustomPreorder.DoesNotExist:
			return []

	def __unicode__(self):
		return "Profile of %s" % self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	""" Automatically create UserProfile object for new users """
	if created:
		UserProfile.objects.get_or_create(user=instance)

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
		verbose_name = "Ticket"

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
		try:
			return float(self.stats_preordered()) / float(PreorderPosition.objects.all().count()) * 100
		except ZeroDivisionError:
			return 0

class Merchandise(models.Model):
	name = models.CharField(verbose_name="Product Name", max_length=255)
	preview_image = models.URLField(verbose_name="URL to preview image", blank=True, null=True)
	detail_url = models.URLField(verbose_name="Link to detail page", blank=True, null=True)
	detail_text = models.CharField(verbose_name="Short detail text (will be linked if detail URL is set", max_length=200, blank=True, null=True)
	active = models.BooleanField(verbose_name="On Sale?", default=True)

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = "Merchandise type"

class Tshirt(CustomPreorderTicket):
	merchandise = models.ForeignKey(Merchandise)
	size = models.CharField(verbose_name="T-Shirt Size", max_length=10)
	type = models.CharField(verbose_name="T-Shirt Type (girly, etc.)", max_length=255)

	class Meta:
		verbose_name = "Merchandise object"

class PreorderPosition(PreorderPosition):
	@property
	def custom_preorder(self):
		return CustomPreorder.objects.get(pk=self.preorder.pk)

	@property
	def is_billing_document(self):
		"""
		checks if this ticket may also function as a legal proof of
		purchase/payment, aka invoice
		"""
		if self.ticket.price == 0:
			return True
		if self.custom_preorder.get_billing_address():
			return True
		return False

class CustomPreorder(Preorder):

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

	def get_billing_address(self):
		try:
			return PreorderBillingAddress.objects.get(preorder=self)
		except PreorderBillingAddress.DoesNotExist:
			return False

	class Meta:
		verbose_name = "Preorder"

class PreorderBillingAddress(models.Model):
	preorder = models.ForeignKey('CustomPreorder', verbose_name="Preorder")
	invoice_id = models.PositiveIntegerField(verbose_name="Invoice ID (\"Rechnungsnummer\")")
	company = models.CharField(verbose_name="Company", blank=True, null=True, max_length=255)
	firstname = models.CharField(verbose_name="First name", blank=False, null=False, max_length=255)
	lastname = models.CharField(verbose_name="Last name", blank=False, null=False, max_length=255)
	address1 = models.CharField(verbose_name="Address 1", blank=False, null=False, max_length=255)
	address2 = models.CharField(verbose_name="Address 2", blank=True, null=True, max_length=255)
	city = models.CharField(verbose_name="City", blank=False, null=False, max_length=255)
	zip = models.CharField(verbose_name="ZIP", blank=False, null=False, max_length=255)
	country = models.CharField(verbose_name="Country", blank=False, null=False, max_length=255)

	@property
	def invoice_number(self):
		return settings.EVENT_DAAS_INVOICE_NUMBER_FORMAT % ({'invoice_id': self.invoice_id})
