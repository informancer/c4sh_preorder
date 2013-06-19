from passbook.models import Pass, EventTicket, Barcode, StoreCard, BarcodeFormat, Location

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
	passfile.barcode.altText = args['uuid'][:13]

	loc = Location(args['lat'], args['long'])
	passfile.locations = [loc,]
	passfile.relevantDate = args['relevant_date']

	passfile.addFile('icon.png', open('%s/icon.png' % args['filespath'], 'r'))
	passfile.addFile('logo.png', open('%s/logo.png' % args['filespath'], 'r'))
	passfile.addFile('logo@2x.png', open('%s/logo@2x.png' % args['filespath'], 'r'))
	passfile.addFile('background.png', open('%s/background.png' % args['filespath'], 'r'))
	passfile.addFile('background@2x.png', open('%s/background@2x.png' % args['filespath'], 'r'))

	return passfile.create('%s/certificate.pem' % args['filespath'], '%s/key.pem' % args['filespath'], '%s/wwdr.pem' % args['filespath'], args['password'])
