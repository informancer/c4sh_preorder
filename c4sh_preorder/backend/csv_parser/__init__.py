import importlib
import csv

class Status:
	"""
	Status:
	* Failure: Parser was unable to find a valid reference hash
	* Success: Parser was able to find a valid reference hash
	"""
	Failure, Success = range(2)

def parse(csv_file, engine, delimiter):
	try:
		parser = importlib.import_module("c4sh_preorder.backend.csv_parser.%s" % engine)
	except:
		raise Exception("No valid CSV parser engine found")

	csv_reader = csv.reader(csv_file, delimiter=delimiter)

	rows = []

	# CSV parser should return a list with
	# a ((enum)Status, (datetime)datetime, (str)name, (str)reason, (str)reference, Decimal(value)) tuple

	for row in csv_reader:
		result = parser.parse_row(row)
		if result:
			rows.append(result)

	return rows
