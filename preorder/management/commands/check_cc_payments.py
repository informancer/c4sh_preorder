from django.core.management.base import BaseCommand, CommandError
from c4sh_preorder.preorder.models import CustomPreorder
from django.db.models import Q, F
from django.core.mail import send_mail, mail_admins
import c4sh_preorder.settings as settings
import datetime
import logging

class Command(BaseCommand):
	help = 'Asks the cc payment API for payment status'

	def handle(self, *args, **options):
		preorders = CustomPreorder.objects.filter(~Q(transaction_id=""))

		logger = logging.getLogger(__name__)
		logger.info("=========== FETCHING CC STATUS ==")
		logger.info(str(datetime.datetime.now()))

		for preorder in preorders:
			status = preorder.get_cc_transaction_status()

			logger.info("Preorder # %s" % preorder.pk)
			logger.info("API Status: %s" % status['data']['status'])

			if status['data']['status'] == "closed":
				if preorder.paid == True:
					continue
				else:
					preorder.paid = True
					preorder.paid_time = datetime.datetime.now()
					preorder.paid_via = "CC"
					preorder.save()
					send_mail("[%s] Update notification" % settings.EVENT_NAME_UNIX, settings.EVENT_PAYMENT_ACK_MAIL_TEXT, "%s <%s>" % (settings.EVENT_NAME_UNIX, settings.EVENT_CONTACT_MAILTO), (preorder.get_user().email,))
			elif status['data']['status'] == "pending":
				# still pending - we cannot do anything
				pass
			elif status['data']['status'] == "open":
				# still open - we cannot do anything
				pass
			elif status['data']['status'] == "refunded":
				# refund! - mail admins!
				mail_admins("CC REFUND", "The following payment has been marked as refunded by PAYMILL:\n\nTransaction ID:%s\nPreorder ID:%s" % (preorder.transaction_id, preorder.pk))
				preorder.paid = False
				preorder.paid_time = ""
				preorder.paid_via = "REFUNDED"
				preorder.save()

		logger.info("== FETCHING CC STATUS =========== ")