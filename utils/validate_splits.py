import argparse
from aggregator import get_stats, count_overlap_source

def main():
	parser = argparse.ArgumentParser(description='Get paths for different categories.')

	# Define arguments for each category
	parser.add_argument('-test', type=str, help='Path for test data')
	parser.add_argument('-all', type=str, help='Path for all data')
	parser.add_argument('-val', type=str, help='Path for validation data')
	parser.add_argument('-train', type=str, help='Path for train data')

	args = parser.parse_args()

	with open(args.all, "r") as f:
		full = f.read().splitlines()[1:]

	with open(args.test, "r") as f:
		test = f.read().splitlines()[1:]

	with open(args.val, "r") as f:
		val = f.read().splitlines()[1:]

	if type(args.train) == str:
		with open(args.train, "r") as f:
			train = f.read().splitlines()[1:]
	else:
		train = []

	# check if there are duplicates in individual files
	if len(set(test)) < len(test):
		print("Test file contains duplicates.")
	elif len(set(val)) < len(val):
		print("Test file contains duplicates.")
	elif len(set(train)) < len(train):
		print("Train file contains duplicates.")
	else:
		print("==== No duplicates found in individual files.")

	# check how many source sentences overlap across test and val
	print("==== %s instances overlap in train-test source sentences."%count_overlap_source(test, train))
	print("==== %s instances overlap in train-val source sentences."%count_overlap_source(val, train))
	print("==== %s instances overlap in test-val source sentences."%count_overlap_source(test, val))
	print("==== %s instances overlap in full-val source sentences."%count_overlap_source(val, full))

	print("All set stats (%s instances):"%len(full))
	for i, j in get_stats(full).items():
		print(i, j)
	print()
	print("Test set stats (%s instances):"%len(test))
	for i, j in get_stats(test).items():
		print(i, j)
	print()
	print("Valid set stats (%s instances):"%len(val))
	for i, j in get_stats(val).items():
		print(i, j)
	print()
	print("Train set stats (%s instances):"%len(train))
	for i, j in get_stats(train).items():
		print(i, j)

if __name__ == '__main__':
	main()


'''
-test final/SDH-en-fa-sdh-test.tsv -val final/SDH-en-fa-sdh-val.tsv -all final/SDH-en-fa-sdh.tsv
python3 validate_splits.py -train final/SDH-train.tsv -test final/SDH-test.tsv -val final/SDH-val.tsv -all final_spreadsheets/SDH-en-fa-sdh.tsv
python3 validate_splits.py -train final/GLK-train.tsv -test final/GLK-test.tsv -val final/GLK-val.tsv -all final_spreadsheets/GLK-en-fa-glk.tsv
python3 validate_splits.py -train final/MZN-train.tsv -test final/MZN-test.tsv -val final/MZN-val.tsv -all final_spreadsheets/MZN-en-fa-mzn.tsv
python3 validate_splits.py -train final/LKI-train.tsv -test final/LKI-test.tsv -val final/LKI-val.tsv -all final_spreadsheets/LKI-en-fa-lki.tsv
python3 validate_splits.py -train final/HAC-train.tsv -test final/HAC-test.tsv -val final/HAC-val.tsv -all final_spreadsheets/HAC-en-fa-hac.tsv

python3 validate_splits.py -test final/TLY-test.tsv -val final/TLY-val.tsv -all final_spreadsheets/TLY-en-fa-tly.tsv
python3 validate_splits.py -test final/BQI-test.tsv -val final/BQI-val.tsv -all final_spreadsheets/BQI-en-fa-bqi.tsv
'''