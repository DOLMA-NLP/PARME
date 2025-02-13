from GlotScript import sp
import re
import Levenshtein
from nltk.tokenize import word_tokenize
import string
import torch
import random
import json
random.seed(42)
from sentence_transformers import SentenceTransformer # https://www.sbert.net/docs/quickstart.html#sentence-transformer
model = SentenceTransformer("all-MiniLM-L6-v2")


'''
	corpus selection
	# First, run the script to create the first batch (randomly) and the second one based on the proposed procedure.
	# Then, import the created batches in a spreadsheet, normalize the values and then sort based on the value of semantic similarity \\ edit distance (normalized)
	# Use the N first rows of the spreadsheet to create other corpora.

	# calculate the average length of the sentences (S_a) in the first batch 
	# then, we calculating the average edit distance for a given sentence in comparison to the first batch,
	# take the average length into account by randomly selecting S_a tokens in the pool of sentence.
	# This will penalize the edit distance calculation based on length as lengthier sentences when compared to smaller ones, 
	# return bigger edit distance values.
'''

def contains_ellipsis(sentence):
	# Pattern to match ellipsis (both ... and . . .)
	ellipsis_pattern = r'\.\.\.|(\. ){2}\.|;|:'
	
	# Check if the pattern exists in the sentence
	if re.search(ellipsis_pattern, sentence):
		return True
	else:
		return False

def remove_outer_quotes(sentence):
	# Remove quotes from the start
	while sentence and sentence[0] in ['"', "'"]:
		sentence = sentence[1:]
	
	# Remove quotes from the end
	while sentence and sentence[-1] in ['"', "'"]:
		sentence = sentence[:-1]
	
	return sentence

def check_sentence(text, script) -> bool:
	# check code-switching
	try:
		if script in sp(text)[-1]["details"] and sp(text)[-1]["details"][script] == 1:
			return True
	except:
		return False
	return False

def contains_named_entity(sentence: str, language="English") -> bool:
	if language == "English":
		capitalized_words = re.findall(r'\b[A-Z][a-z]*\b', sentence)
		# Exclude the pronoun 'I'
		capitalized_words = [word for word in capitalized_words if word != 'I']

		return bool(capitalized_words) and not sentence.isupper()
	elif language == "Persian":
		if any([True if i in named_entities else False for i in remove_punctuation(sentence).split()]):
			return True
	return False

def remove_punctuation(text: str) -> str:
	arabic_punctuation = "،؛؟٪"
	# Combining with English punctuation
	all_punctuation = arabic_punctuation + string.punctuation
	translation_table = str.maketrans('', '', all_punctuation)
	
	return text.translate(translation_table)

def average_edit_distance(new_sentence: str, corpus: list) -> float:
	if not corpus:
		return 0.0  # Return 0 if the list is empty

	length_list = list()
	# remove punctuation marks
	new_sentence_no_punt = remove_punctuation(new_sentence)
	
	# calculate the average length of the corpus in the corpus
	average_corpus_length = int(sum([len(remove_punctuation(i)) for i in corpus]) / len(corpus))

	for candidate in corpus:
		candidate_no_punt = remove_punctuation(candidate)

		# find the smaller length
		if len(new_sentence_no_punt) >= average_corpus_length and len(candidate_no_punt) >= average_corpus_length:
			comparison_length = average_corpus_length
		elif len(new_sentence_no_punt) < average_corpus_length and len(candidate_no_punt) >= average_corpus_length:
			comparison_length = len(new_sentence_no_punt)
		elif len(new_sentence_no_punt) >= average_corpus_length and len(candidate_no_punt) < average_corpus_length:
			comparison_length = len(candidate_no_punt)
		else:
			comparison_length = min(len(new_sentence_no_punt), len(candidate_no_punt))

		length_list.append(Levenshtein.distance(random.sample(new_sentence_no_punt, comparison_length), 
							random.sample(candidate_no_punt, comparison_length)))

	# total_distance = sum(Levenshtein.distance(new_sentence, sentence) for sentence in corpus)
	total_distance = sum(length_list)
	average_distance = total_distance / len(corpus)

	return average_distance

def valid_sentence(sentence: str, t_sentence: str, source_script, target_script) -> bool:
	# not contains_named_entity(sentence, "Persian") and 
	if len(sentence.split()) > 2 and len(t_sentence.split()) > 2 and not sentence.isupper() and not t_sentence.isupper():
		if (check_sentence(sentence, source_script) and check_sentence(t_sentence, target_script) and 
			not contains_named_entity(t_sentence) and 
			not contains_ellipsis(sentence) and not contains_ellipsis(t_sentence) and 
			sentence[0:2] != "و " and t_sentence[0:3] != "and"): 
			return True
	return False

def sorting_key(item):
	# sorting key to sort by highest edit distance on the source language side 
	# and then by the lowest semantic similarity on the target language side
    a, b = item[1]
    return (-a, b)

def normalize_multiply(batch):
	distances = [value[0] for value in batch.values()]

	# Min-max normalization of distances
	min_distance = min(distances)
	max_distance = max(distances)
	normalized_distances = {
		key: (value[0] - min_distance) / (max_distance - min_distance)
		for key, value in batch.items()
	}

	# Multiply normalized distance by the similarity
	normalized_batch = {
		key: normalized_distances[key] / value[1] # *
		for key, value in batch.items()
	}

	return normalized_batch

def main(file_config):

	with open(file_config["source_file"], "r") as f:
		source = f.read().splitlines()

	with open(file_config["target_file"], "r") as f:
		target = f.read().splitlines()

	zipped_list = list(zip(source, target))
	random.shuffle(zipped_list)
	
	selected_source, selected_target = list(), list()
	new_batch, final_batch = dict(), dict()
	second_file, final_file = list(), list()
	corpus_embeddings_loaded = False
	first_batch_size, search_size, final_batch_size = 3500, 5000, 15000
	counter = 0
	top_candidate_number = 3500
	corpus_updated = False

	for index, (sentence, t_sentence) in enumerate(zipped_list):
		# clean sentence
		sentence, t_sentence = remove_outer_quotes(sentence.strip()), remove_outer_quotes(t_sentence.strip())

		# first batch
		if counter < first_batch_size:
			# randomly select sentences
			if valid_sentence(sentence, t_sentence, file_config["source_script"], file_config["target_script"]):
				counter += 1
				selected_source.append(sentence)
				selected_target.append(t_sentence)
				print("\t".join([str(counter), sentence, t_sentence]))

		# second batch
		elif first_batch_size <= counter and counter < first_batch_size + search_size:# (counter > first_batch_size and counter < search_size) or (not first_run and counter < final_batch_size):
			if valid_sentence(sentence, t_sentence, file_config["source_script"], file_config["target_script"]):
				
				print("\t".join([str(counter), sentence, t_sentence]))

				# if not first_run and index < search_size:
				# 	continue

				if sentence in selected_source:
					print("heye")
				# calculate distance
				distance = average_edit_distance(sentence, selected_source)

				# calculate the average similarity score
				if not corpus_embeddings_loaded:
					corpus_embeddings = model.encode(selected_target)
					corpus_embeddings_loaded = True

				sentence_embedding = model.encode(t_sentence)
				similarities = model.similarity(corpus_embeddings, sentence_embedding)
				average_similarity = torch.mean(similarities).item()

				new_batch.update({(sentence, t_sentence) : (distance, average_similarity)})
				counter += 1
		
		elif counter >= first_batch_size + search_size and counter < final_batch_size:
			# update and save the previous batches
			if not corpus_updated:
				# save the first batch
				with open(file_config["saving_dir"] + "first_batch.tsv", "w") as f:
					f.write("\n".join([i + "\t" + j for i, j in zip(selected_source, selected_target)]))

				# Extract all edit distances
				normalized_new_batch = normalize_multiply(new_batch)
				sorted_normalized_batch = dict(sorted(normalized_new_batch.items(), key=lambda item: item[1], reverse=True)[: top_candidate_number])

				for i in sorted_normalized_batch:
					selected_source.append(i[0])
					selected_target.append(i[1])
				
				normalized_new_batch = sorted(normalized_new_batch.items(), key=lambda item: item[1], reverse=True)

				for i in normalized_new_batch:
					second_file.append(i[0][0] + "\t" + i[0][1] + "\t" + str(i[1]))#str(normalized_new_batch[i][0]) + "\t" + str(normalized_new_batch[i][1]))

				# save the second batch
				with open(file_config["saving_dir"] + "second_batch.tsv", "w") as f:
					f.write("\n".join(second_file))

				corpus_updated = True

			# create the final batch
			if valid_sentence(sentence, t_sentence, file_config["source_script"], file_config["target_script"]):
				
				print("\t".join([str(counter), sentence, t_sentence]))

				if sentence in selected_source:
					print("heye")

				# calculate distance
				distance = average_edit_distance(sentence, selected_source)

				# calculate the average similarity score
				if not corpus_embeddings_loaded:
					corpus_embeddings = model.encode(selected_target)
					corpus_embeddings_loaded = True

				sentence_embedding = model.encode(t_sentence)
				similarities = model.similarity(corpus_embeddings, sentence_embedding)
				average_similarity = torch.mean(similarities).item()

				final_batch.update({(sentence, t_sentence) : (distance, average_similarity)})
				counter += 1
			
		
	normalized_final_batch = normalize_multiply(final_batch)
	normalized_final_batch = sorted(normalized_final_batch.items(), key=lambda item: item[1], reverse=True)
	# sorted_normalized_final_batch = dict(sorted(normalized_final_batch.items(), key=lambda item: item[1], reverse=True)[: top_candidate_number])

	for i in normalized_final_batch:
		final_file.append(i[0][0] + "\t" + i[0][1] + "\t" + str(i[1]))#str(normalized_final_batch[i][0]) + "\t" + str(normalized_final_batch[i][1]))

	with open(file_config["saving_dir"] + "final_batch.tsv", "w") as f:
		f.write("\n".join(final_file))

	print("All saved :-)")

if __name__ == "__main__":

	# files = {
	# 	# "TEP-fa-en":
	# 	# {	
	# 	# 	"source_script": "Arab",
	# 	# 	"target_script": "Latn",
	# 	# 	"source_file": "/Users/sina/Bucket/Parallel/TEP/en-fa.txt/TEP.en-fa.fa",
	# 	# 	"target_file": "/Users/sina/Bucket/Parallel/TEP/en-fa.txt/TEP.en-fa.en"
	# 	# }
	# 	"Mizan-fa-en":
	# 	{	
	# 		"source_script": "Arab",
	# 		"target_script": "Latn",
	# 		"source_file": "/Users/sina/Bucket/Parallel/Mizan/en-fa.txt/MIZAN.en-fa.fa",
	# 		"target_file": "/Users/sina/Bucket/Parallel/Mizan/en-fa.txt/MIZAN.en-fa.en",
	# 		"named_entity_list": "/Users/sina/Bucket/Datasets/Persian-NER_all.txt",
	# 		"saving_dir": "corpora/EN-FA/"
	# 	}
	# }
	with open("data.json", "r") as f:
		files = json.load(f)
		
	for file_config in files:
		main(file_config)
	# with open(file_config["named_entity_list"], "r") as f:
	# 	named_entities = set([i.split("\t")[0] for i in f.read().splitlines()])












