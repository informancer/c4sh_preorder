# encoding: utf-8

import json
from django.conf import settings
import requests

def request(func, *args):
	payload = json.dumps({
		"method": func,
		"params": args,
		"id": 1
		})
	headers = {'content-type': 'application/json'}
	url = settings.EVENT_DAAS_API_BASE+settings.EVENT_DAAS_API_ENDPOINT
	r = requests.post(url, data=payload, headers=headers)
	return r.json().get("result", r.json().get("error"))

def download(url, target):
	r = requests.get(settings.EVENT_DAAS_API_BASE+url, stream=True)
	with open(target, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
				f.flush()
	return target

def generate_invoice(preorder):
	billingaddress = preorder.get_billing_address()
	payload = {
		"invoice_number": billingaddress.invoice_number,
		"reference_hash": settings.EVENT_PAYMENT_PREFIX+'-'+preorder.get_reference_hash(),
		"firstname": billingaddress.firstname,
		"lastname": billingaddress.lastname,
		"company": billingaddress.company,
		"address1": billingaddress.address1,
		"address2": billingaddress.address2,
		"zip": billingaddress.zip,
		"city": billingaddress.city,
		"country": billingaddress.country,
		"cart": [],
	}
	for item in preorder.get_tickets():
		payload["cart"].append({
			"amount": item['amount'],
			"name": item['t'].name,
			"value": str(item['t'].price).replace(".", ",")
			})
	result = request("generate", "rechnung", payload)
	if not result or type(result) == str:
		return False
	filename = download(result.get("url"), billingaddress.get_invoice_filename(check_existence=False))
	return filename
