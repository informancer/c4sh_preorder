from passbook.models import Pass, EventTicket, Barcode, StoreCard, BarcodeFormat

def make_passbook_file(args={}):
	cardInfo = EventTicket()
	cardInfo.addPrimaryField('eventName', args['ticket'], 'Ticket')
	cardInfo.addSecondaryField('doorsOpen', args['from'], 'From')
	cardInfo.addSecondaryField('doorsClose', args['to'], 'To')

	passfile = Pass(cardInfo, passTypeIdentifier=args['identifier'], organizationName=args['organisation'], teamIdentifier=args['teamidentifier'])

	passfile.description = args['desc']
	passfile.backgroundColor = args['bgcolor']
	passfile.foregroundColor = args['fgcolor']
	passfile.logoText = args['logotext']
	passfile.serialNumber = args['uuid']
	passfile.barcode = Barcode(message=args['uuid'], format=BarcodeFormat.QR)
	passfile.barcode.altText = args['uuid']

	passfile.addFile('icon.png', open('%s/logo.png' % args['filespath'], 'r'))
	passfile.addFile('logo.png', open('%s/logo.png' % args['filespath'], 'r'))

	return passfile.create('%s/certificate.pem' % args['filespath'], '%s/key.pem' % args['filespath'], '%s/wwdr.pem' % args['filespath'], args['password'])