import re
import unicodedata

file_name = ["/Users/sina/Bucket/Corpora/Corpus_sdh/sdh-all.txt", "/Users/sina/Bucket/Corpora/Corpus_zza_hac/hac-all.txt", "/Users/sina/Bucket/Corpora/Corpus_zza_hac/zza-all.txt"][-1]
lang_code = ["HAC", "SDH", "ZZA"][-1]

with open(file_name, "r") as f:
	corpus = f.read()

def extract_sentences(text):
	# Remove anything before and including the '/', '-', or ':' character in each sentence
	text = re.sub(r'.*?[\/\-:]', '', text)

	# This regex pattern matches sentence-ending punctuation followed by a space or end of string
	sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\n|\،|\؟|\؛)\s')

	sentences = sentence_endings.split(text)
	
	# cleaning to handle cases where the text doesn't adhere to strict punctuation
	cleaned_sentences = []
	for sentence in sentences:
		# Removing leading and trailing spaces
		sentence = sentence.strip()
		
		if sentence:
			# Check for allowed punctuation and Latin characters
			if not re.search(r'[^?!.,;:،؟؛\s\w]', sentence) and not re.search(r'[A-Za-z]', sentence):
				# Skip sentences containing Arabic diacritics
				if not re.search(r'[\u064B-\u065F]', sentence):
					# Skip sentences with double dots
					if '..' not in sentence:
						# Ensure the sentence is clean (contains only Arabic script and allowed punctuation)
						if re.match(r'^[\u0600-\u06FF\s\.\,\?\!؛:،؟]+$', sentence):
							cleaned_sentences.append(sentence.strip())
	
	return cleaned_sentences

def contains_digits(text):
	for i in "0123456789٠١٢٣٤٥٦٧٨٩":
		if i in text:
			return True
	return False


def extract_sentences_zazaki(text):
	# Step 1: Split the text into sentences
	sentences = re.split(r'(?<=[.!?]) +', corpus)
	
	def is_valid_sentence(sentence):
		# Step 2: Check if the sentence contains any capitalized word except the first word
		# and if it contains any digits
		words = sentence.split()
		for word in words[1:]:
			if word[0].isupper() or any(char.isdigit() for char in word):
				return False
		return True

	def clean_sentence(sentence):
		# Step 3: Remove initial quotation parts if they exist
		if ':' in sentence:
			# Find the last colon before a space or punctuation to consider as the end of the initial part
			parts = sentence.split(':', 1)
			sentence = parts[-1].strip()
		return sentence
	
	valid_sentences = []
	
	for sentence in sentences:
		sentence = sentence.strip()
		if is_valid_sentence(sentence):
			cleaned_sentence = clean_sentence(sentence)
			valid_sentences.append(cleaned_sentence)
	
	return valid_sentences

def is_valid(text):
	if '\t' not in text and "“" not in text and "”" not in text and len(text) < 200 and len(text) > 5 and "…" not in text and "\"" not in text and ".." not in text \
		and "(" not in text and ")" not in text and "-" != text[0] and "," not in text:
		return True
	return False

if lang_code == "ZZA": 
	sentences = [i for i in list(set(extract_sentences_zazaki(corpus))) if len(i.split()) > 1 and is_valid(i)]
else:
	sentences = [i.replace("!.", ".") for i in list(set(extract_sentences(corpus))) if i[-1] == "." and len(i) < 200 and not contains_digits(i) and len(i.split()) > 1]

print("Number of sentences:", len(sentences))

with open("corpora/%s/%s_sentences.txt"%(lang_code, lang_code), "w") as f:
	f.write("\n".join(sentences))
