from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from settings import DEFAULT_FROM_EMAIL

def c4shmail(to, subject, template, data):
	plaintext = get_template('emails/%s.txt' % template)
	text_content = plaintext.render(data)
	msg = EmailMultiAlternatives(subject, text_content, DEFAULT_FROM_EMAIL, [to])
	msg.send()