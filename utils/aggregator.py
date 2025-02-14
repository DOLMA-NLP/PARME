"""
	This script creates a benchmark for MT evaluation and training based on individual tsv files.
	It is run after the "process.py" script where the most common sentences across datasets are extracted.
	This script selects the first 1000 sentences for each language in "common_sentences.py" and then, 
	aligns them to the original spreadsheets.

	This generates the train/val/test datasets with complete metadata.

	-- DOLMA-NLP
"""

import json

def count_overlap_source(dataset_1: list, dataset_2: list) -> int:
	# given two datasets containing parallel sentences, count the number of source sentences that are common in the two datasets
	sources_1 = {line.split("\t")[0] for line in dataset_1}
	sources_2 = {line.split("\t")[0] for line in dataset_2}

	# Find the intersection of the two sets
	overlap = sources_1 & sources_2

	# Return the number of common source sentences
	return len(overlap)


def get_stats(dataset: list):
	dialects = {}
	orthography = {}
	translators = {}
	dialect_orthography = {}

	for j in dataset:
		dialect = j.split("\t")[3]
		ortho = j.split("\t")[5]
		translator = j.split("\t")[6]
		
		dialects[dialect] = dialects.get(dialect, 0) + 1
		
		# Update orthography count
		orthography[ortho] = orthography.get(ortho, 0) + 1
		
		# Update translators count
		translators[translator] = translators.get(translator, 0) + 1
		
		# Update dialect_orthography count
		if dialect not in dialect_orthography:
			dialect_orthography[dialect] = {}
		
		# Initialize or increment the orthography count for this dialect
		dialect_orthography[dialect][ortho] = dialect_orthography[dialect].get(ortho, 0) + 1

	return {"dialects": dialects, "orthography": orthography, "translators": translators, "dialect_orthography": dialect_orthography}

if __name__ == "__main__":
	files = {
		"SDH": "spreadsheets/SDH-en-fa-sdh.tsv",
		"GLK": "spreadsheets/GLK-en-fa-glk.tsv",
		"MZN": "spreadsheets/MZN-en-fa-mzn.tsv",
		"TLY": "spreadsheets/TLY-en-fa-tly.tsv",
		"LKI": "spreadsheets/LKI-en-fa-lki.tsv",
		"BQI": "spreadsheets/BQI-en-fa-bqi.tsv",
		"HAC": "spreadsheets/HAC-en-fa-hac.tsv"
	}

	stats_file = dict()
	for lang_code in files:
		print("Processing " + lang_code)

		with open(files[lang_code]) as f:
			content = f.read().splitlines()

		with open(f"common_sentences.tsv") as f:
			common_sentences = f.read().splitlines()[1:]


		##### GET A SUMMARY OF THE DATASET
		if lang_code not in stats_file:
			stats_file.update({lang_code: {"all": {},
				"test": {},
				"valid": {},
				"test": {}
				}})

		print("All dataset report:  ====================")
		stats_file[lang_code]["all"] = get_stats(content[1:])
		for i, j in get_stats(content[1:]).items():
			print(i, j)
		print()

		##### FILTER NON-REDUNDANT INSTANCES
		preselected = list()
		source_sentences = [i.split("\t")[0] for i in content[1:]]
		for i in content[1:]:
			# the sentence should have only appeared once in the data
			if source_sentences.count(i.split("\t")[0]) == 1 and preselected.count(i.split("\t")[0]) == 0:
				preselected.append(i)

		print("Number of sentences:", len(content[1:]))
		print("Number of sentences filtered out:", len(preselected))

		##### SELECT SENTENCES FOR TEST AND VAL SETS
		indices = {"EN": 0, "FA": 1, "GLK": 2, "MZN": 3, "TLY": 4, "LKI": 5, "BQI": 6, "HAC": 7, "SDH": 8}
		test_content, val_content, train_content = dict(), dict(), list()
		num_dialects = len(get_stats(content[1:])["dialects"])
		distributions = {"SDH": {
			"test": {'Pehley':200, 'Garusi':0, 'Kalhori':200, 'Kirmashani':541, 'Badrei':200},
			"valid": {'Pehley':200, 'Garusi':0, 'Kalhori':0, 'Kirmashani':800, 'Badrei':0}
			},
			"GLK":{"test": {'Western Gilaki': 500, 'Eastern Gilaki': 500}, "valid":{'Western Gilaki': 500, 'Eastern Gilaki': 500}},
			"MZN":{"test": {"Central Mazani": 1000}, "valid":{"Central Mazani": 1000}},
			"TLY":{"test": {"Southern Talysh": 1000}, "valid":{"Southern Talysh": 1200}},
			"LKI":{"test": {"Kakavandi": 586, "Jalalvan / Hozmanvan": 200, "Sahneyi": 214}, "valid":{"Kakavandi": 787, "Jalalvan / Hozmanvan": 213, "Sahneyi": 0}},
			"BQI":{"test": {"Luri Bakhtiari (Central)": 1000}, "valid":{"Luri Bakhtiari (Central)": 998}},
			"HAC":{"test": {"Lhon": 333, "Jawaru": 333, "Hawraman Takht": 333}, "valid":{"Lhon": 333, "Jawaru": 333, "Hawraman Takht": 333}}
		}
		included_instances = list()
		for mode in ["test", "valid"]:
			temp_var = dict()
			for i in common_sentences:
				# filter specific orthographies
				# check if the sentence exists for the target language
				if len(i.split("\t")[indices[lang_code]]):
					row = "\t".join((i.split("\t")[0], i.split("\t")[1], i.split("\t")[indices[lang_code]]))

					for j in preselected:
						if lang_code == "GLK" and j.split("\t")[5] not in ["Vrg"]:
							continue
						if lang_code == "SDH" and j.split("\t")[5] not in ["Southern Kurdish"]:
							continue
						if lang_code == "MZN" and j.split("\t")[5] not in ["Farsi"]:
							continue
						if lang_code == "HAC" and j.split("\t")[5] not in ["Hawrami"]:
							continue

						if row in j:
							dialect_label = j.split("\t")[3]
							# if len(included_instances) <= 1000:
							if dialect_label not in temp_var:
								temp_var.update({dialect_label: []})

							if mode == "test":
								if len(temp_var[dialect_label]) < distributions[lang_code][mode][dialect_label] and j not in included_instances and len(included_instances) <= 1000:#1000 / num_dialects:
									temp_var[dialect_label].append(j)
									included_instances.append(j)
							else:
								# if len(temp_var[dialect_label]) < 1000 / num_dialects and j not in included_instances:
								if len(temp_var[dialect_label]) < distributions[lang_code][mode][dialect_label] and j not in included_instances and len(included_instances) <= 2000:#1000 / num_dialects:
									temp_var[dialect_label].append(j)
									included_instances.append(j)
			if mode == "test":
				test_content = temp_var
			else:
				val_content = temp_var

		# ============================================================================
		print("==================== Test set report:")
		test_content = [item for sublist in test_content.values() for item in sublist]
		stats_file[lang_code]["test"] = get_stats(test_content)
		print("Size:", len(test_content))
		for i, j in get_stats(test_content).items():
			print(i, j)
		print()
		
		test_content.insert(0, "\t".join(content[0].split("\t")[0:-1]))
		with open("final/%s-test.tsv"%lang_code, "w") as f:
			f.write("\n".join(test_content))

		print("==================== Val set report:")
		val_content = [item for sublist in val_content.values() for item in sublist]
		stats_file[lang_code]["valid"] = get_stats(val_content)
		print("Size:", len(val_content))
		for i, j in get_stats(val_content).items():
			print(i, j)
		print()
		
		val_content.insert(0, "\t".join(content[0].split("\t")[0:-1]))
		with open("final/%s-val.tsv"%lang_code, "w") as f:
			f.write("\n".join(val_content))

		##### ADD ANYTHING NOT INCLUDED IN THE TEST AND VAL SETS TO THE TRAIN SET
		for i in content[1:]:
			if i not in test_content and i not in val_content:
					train_content.append(i)

		print("==================== Train set report:")
		stats_file[lang_code]["train"] = get_stats(train_content)
		print("Size:", len(train_content))
		for i, j in get_stats(train_content).items():
			print(i, j)
		print()

		train_content.insert(0, "\t".join(content[0].split("\t")[0:-1]))
		with open("final/%s-train.tsv"%lang_code, "w") as f:
			f.write("\n".join(train_content))

	# SAVE THE STATS FILE
	# with open("datasets_stats.json", "w", encoding='utf-8') as f:
	# 	json.dump(stats_file, f, ensure_ascii=False, indent=4)
	
