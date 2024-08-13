import random
import json
random.seed(42)

import create_corpus

with open("data.json", "r") as f:
	files = json.load(f)

# if there are certain sentences to ignore, add
ignore_sentences = list()
with open("corpora/EN-FA/Reference-en-fa.tsv", "r") as f:
	for i in f.read().splitlines():
		ignore_sentences.append(i.split("\t")[0].strip())
		ignore_sentences.append(i.split("\t")[1].strip())

ignore_sentences = list(set(ignore_sentences))

sample_size = 20000
for file_config in files:
	with open(files[file_config]["source_file"], "r") as f:
		source = f.read().splitlines()

	with open(files[file_config]["target_file"], "r") as f:
		target = f.read().splitlines()

	zipped_list = list(zip(source, target))
	random.shuffle(zipped_list)
	
	selected_source, selected_target = list(), list()
	counter = 0

	for index, (sentence, t_sentence) in enumerate(zipped_list):
		# clean sentence
		sentence, t_sentence = create_corpus.remove_outer_quotes(sentence.strip()), create_corpus.remove_outer_quotes(t_sentence.strip())

		# first batch
		if counter < sample_size:
			# randomly select sentences
			if create_corpus.valid_sentence(sentence, t_sentence, files[file_config]["source_script"], files[file_config]["target_script"]) \
				and sentence not in ignore_sentences and t_sentence not in ignore_sentences and len(sentence.split()) > 8:
				selected_source.append(sentence)
				selected_target.append(t_sentence)
				ignore_sentences.append(sentence)
				counter += 1

				# print("\t".join([str(counter), sentence, t_sentence]))
				
	print("average length", sum([len(i.split()) for i in selected_source]) / len(selected_source))

	with open("corpora/EN-FA/random_sample_20k.tsv", "w") as f:
		f.write("\n".join([i + "\t" + j for i, j in zip(selected_source, selected_target)]))