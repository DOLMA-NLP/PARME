import gc
import torch
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

model_size = ["600M", "3.3B"][0]

if model_size == "600M":
	tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
	model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M").cuda()
	output_name = "outputs_600M"
else:
	tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-3.3B")
	model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-3.3B").cuda()
	output_name = "outputs_3.3"

translator = pipeline(
	'translation', 
	model=model, 
	tokenizer=tokenizer, 
	max_length=400, 
	device=0,
	num_beams=3, 
	early_stopping=True
)

datasets = {
	"BQI-arab": "../datasets/BQI-test.tsv",
	"GLK-arab": "../datasets/GLK-test.tsv",
	"HAC-arab": "../datasets/HAC-test.tsv",
	"LKI-arab": "../datasets/LKI-test.tsv",
	"MZN-arab": "../datasets/MZN-test.tsv",
	"SDH-arab": "../datasets/SDH-test.tsv",
	"TLY-arab": "../datasets/TLY-test.tsv",
	"ZZA-latn": "../datasets/ZZA-test.tsv",
	"BQI-latn": "../datasets/BQI-test-trnltr-latn.tsv",
	"GLK-latn": "../datasets/GLK-test-trnltr-latn.tsv",
	"HAC-latn": "../datasets/HAC-test-trnltr-latn.tsv",
	"LKI-latn": "../datasets/LKI-test-trnltr-latn.tsv",
	"MZN-latn": "../datasets/MZN-test-trnltr-latn.tsv",
	"SDH-latn": "../datasets/SDH-test-trnltr-latn.tsv",
	"TLY-latn": "../datasets/TLY-test-trnltr-latn.tsv",
	"ZZA-arab": "../datasets/ZZA-test-trnltr-arab.tsv"
}

####### translate Persian sentences
# print("Translating Farsi...")
# pes_translations = list()
# idx = 0
# with open("/home/user/ahmadi/DOLMA/evaluation/datasets/pes_sentences.txt", "r") as f:
# 	sentences = f.read().splitlines()

# for sentence in sentences:
# 	pes_translations.append(sentence.strip() + "\t" + translator(sentence, src_lang="pes_Arab", tgt_lang="eng_Latn")[0]['translation_text'])
# 	print(f"Processed {idx + 1}/{len(sentences)} rows")
# 	idx += 1
		
# with open("/home/user/ahmadi/DOLMA/evaluation/datasets/pes_sentences_nllb_600M_translated.tsv", "w") as f:
# 	f.write("\n".join(list(set(pes_translations))))

##############################

for lang_code in datasets:
	source_en, source_fa, target = list(), list(), list()
	with open(datasets[lang_code], 'r') as f:
		for i in f.read().splitlines()[1:]:
			source_en.append(i.split("\t")[0])
			if "ZZA" in lang_code:
				source_fa.append([])
				target.append(i.split("\t")[1])
			else:
				source_fa.append(i.split("\t")[1])
				target.append(i.split("\t")[2])

	results = {"target": target, 
				"source_en": source_en,
				"source_fa": source_fa,
				"translations": {"pes_Arab": {"eng_Latn":[], "pes_Arab":[]},
					 "eng_Latn": {"eng_Latn":[], "pes_Arab":[]},
					 "ckb_Arab": {"eng_Latn":[], "pes_Arab":[]},
					 "arb_Arab": {"eng_Latn":[], "pes_Arab":[]},
					 "arb_Latn": {"eng_Latn":[], "pes_Arab":[]},
					 "tur_Latn": {"eng_Latn":[], "pes_Arab":[]},
					 "kmr_Latn": {"eng_Latn":[], "pes_Arab":[]}
				}}
		
	for idx, tgt_text in enumerate(target):
		if "trnltr" in datasets[lang_code]:
			source_languages = ["arb_Latn", "eng_Latn", "tur_Latn", "kmr_Latn"]
		else:
			source_languages = ["pes_Arab", "eng_Latn", "ckb_Arab", "arb_Arab", "tur_Latn", "kmr_Latn"]

		for source_lang in source_languages:
			for target_lang in ["eng_Latn"]:#, "pes_Arab"]:
				print("Processing %s (from %s to %s)..."%(lang_code, source_lang, target_lang))
				try:
					translation = translator(tgt_text, src_lang=source_lang, tgt_lang=target_lang)[0]['translation_text']
					results["translations"][source_lang][target_lang].append(translation)
					print(f"Processed {idx + 1}/{len(target)} rows")
				except Exception as e:
					print(f"Error translating line {idx}: {e}")
					results["translations"][source_lang][target_lang].append("")

	output_file = f"DOLMA/evaluation/{output_name}/{lang_code}.json"
	with open(output_file, 'w', encoding='utf-8') as out_f:
		json.dump(results, out_f, ensure_ascii=False, indent=4)

	print(f"Finished processing {lang_code}. Results saved to {output_file}.")

	# Free up GPU memory
	gc.collect()
	torch.cuda.empty_cache()

