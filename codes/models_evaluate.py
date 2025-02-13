import torch
from transformers import M2M100ForConditionalGeneration, AutoTokenizer
from sacrebleu.metrics import BLEU, CHRF
import pandas as pd
from pathlib import Path
import json
import time
from tqdm import tqdm

# Evaluation script for X>Eng MT models
def load_test_data(file_path, lang_code):
	"""Load test data from TSV file with different formats for ZZA and other languages"""
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			_ = f.readline()  # skip header
			lines = f.readlines()
		
		english_refs = []  # English references
		source_texts = []  # Source language texts
		
		for line in lines:
			parts = line.strip().split('\t')
			if lang_code == "ZZA":
				english_refs.append(parts[0].strip())  # English reference
				source_texts.append(parts[1].strip())  # Zaza text
			else:
				english_refs.append(parts[0].strip())  # English reference
				source_texts.append(parts[2].strip())  # Source language text
		
		print(f"Loaded {len(source_texts)} pairs from {file_path}")
		if len(source_texts) > 0:
			print(f"Sample pair from {lang_code}:")
			print(f"Source text: {source_texts[0]}")
			print(f"English reference: {english_refs[0]}")
			
		return source_texts, english_refs
		
	except Exception as e:
		print(f"Error reading file {file_path}: {str(e)}")
		raise

def translate(model, tokenizer, texts, source_lang, batch_size=8, device="cpu"):
	"""Translate source texts to English"""
	model = model.to(device)
	translations = []
	
	# Set tokenizer languages
	tokenizer.src_lang = source_lang  # Source language
	tokenizer.tgt_lang = "eng_Latn"   # Target is English
	
	# Process in batches with progress bar
	for i in tqdm(range(0, len(texts), batch_size), desc="Translating"):
		batch_texts = texts[i:i + batch_size]
		
		# Tokenize
		inputs = tokenizer(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
		inputs = {k: v.to(device) for k, v in inputs.items()}
		
		# Generate translations
		with torch.no_grad():
			outputs = model.generate(
				**inputs,
				forced_bos_token_id=tokenizer.convert_tokens_to_ids("eng_Latn"),
				max_length=128,
				num_beams=5,
				num_return_sequences=1
			)
		
		# Decode translations
		batch_translations = tokenizer.batch_decode(outputs, skip_special_tokens=True)
		translations.extend(batch_translations)
		
		# Print sample translations from first batch
		if i == 0:
			print("\nSample translations from first batch:")
			for src, tgt in zip(batch_texts[:2], batch_translations[:2]):
				print(f"Source: {src}")
				print(f"Translation: {tgt}\n")
	
	return translations

def evaluate_translations(hypotheses, references):
	"""Calculate BLEU and chrF scores"""
	bleu = BLEU()
	chrf = CHRF()
	
	bleu_score = bleu.corpus_score(hypotheses, [references])
	chrf_score = chrf.corpus_score(hypotheses, [references])
	
	return bleu_score.score, chrf_score.score

def save_translations(sources, references, translations, output_file):
	"""Save all translations to a TSV file"""
	df = pd.DataFrame({
		'source': sources,
		'reference': references,
		'translation': translations
	})
	df.to_csv(output_file, sep='\t', index=False)

def main():
	# Check for CUDA availability
	device = "cuda" if torch.cuda.is_available() else "cpu"
	print(f"Using device: {device}")
	
	# Models to evaluate
	models_dir = Path("/home/user/ahmadi/DOLMA")
	model_paths = [
		"nllb_finetuned_base",
		"nllb_finetuned_augmented",
		"nllb_finetuned_base_I",
		"nllb_finetuned_augmented_I" # here and up are with the ZZA defected
		"nllb_finetuned_base",
		"nllb_finetuned_base_II",
		"nllb_finetuned_augmented_II",
		"nllb_finetuned_base_III"
		"nllb_finetuned_augmented_III",
		"nllb_finetuned_augmented_III"
		"nllb_finetuned_base_II_improved"
	]
	output_dir = Path("evaluation_results")
	# when evaluating on samples
	models_dir = Path("/home/user/ahmadi/DOLMA/nllb_finetuned_samples")
	model_paths = [
		"nllb_finetuned_base_100",
		"nllb_finetuned_base_200",
		"nllb_finetuned_base_300",
		"nllb_finetuned_base_400",
		"nllb_finetuned_base_500",
		"nllb_finetuned_base_600",
		"nllb_finetuned_base_700",
		"nllb_finetuned_base_800",
		"nllb_finetuned_base_900",
		"nllb_finetuned_base_1000"
	]
	
	# when evaluating on samples
	models_dir = Path("/home/user/ahmadi/DOLMA/nllb-finetuned_ablation")
	model_paths = [
		"nllb_finetuned_base_bqi",
		"nllb_finetuned_base_glk",
		"nllb_finetuned_base_hac",
		"nllb_finetuned_base_lki",
		"nllb_finetuned_base_mzn",
		"nllb_finetuned_base_sdh",
		"nllb_finetuned_base_tly",
		"nllb_finetuned_base_zza",
	]
	output_dir = Path("evaluation_results_ablation")

	# Test sets
	test_dir = Path("/home/user/ahmadi/DOLMA/datasets")
	# output_dir = Path("evaluation_results")
	# output_dir = Path("evaluation_results_samples")
	
	output_dir.mkdir(exist_ok=True)
	
	languages = {
		"BQI": "bqi_Arab",
		"GLK": "glk_Arab",
		"HAC": "hac_Arab",
		"LKI": "lki_Arab",
		"MZN": "mzn_Arab",
		"SDH": "sdh_Arab",
		"TLY": "tly_Arab",
		"ZZA": "zza_Latn"
	}
	
	all_results = {}
	
	for model_path in model_paths:
		full_model_path = models_dir / model_path
		print(f"\nEvaluating model: {model_path}")
		
		# Create model-specific output directory
		model_output_dir = output_dir / model_path
		model_output_dir.mkdir(exist_ok=True)
		
		# Load model and tokenizer
		print("Loading model and tokenizer...")
		model = M2M100ForConditionalGeneration.from_pretrained(str(full_model_path))
		tokenizer = AutoTokenizer.from_pretrained(str(full_model_path))
		model.eval()
		
		model_results = {}
		
		for lang_code, nllb_code in languages.items():
			test_file = test_dir / f"{lang_code}-test.tsv"
			print(f"\nProcessing {lang_code} (NLLB code: {nllb_code})")
			
			try:
				# Load test data
				source_texts, english_refs = load_test_data(test_file, lang_code)
				print(f"Loaded {len(source_texts)} test examples")
				
				# Time the translation process
				start_time = time.time()
				
				# Translate to English
				translations = translate(
					model, 
					tokenizer, 
					source_texts,
					source_lang=nllb_code,
					device=device
				)
				
				translation_time = time.time() - start_time
				
				# Calculate scores
				bleu_score, chrf_score = evaluate_translations(translations, english_refs)
				
				# Save all translations
				translations_file = model_output_dir / f"{lang_code}_translations.tsv"
				save_translations(source_texts, english_refs, translations, translations_file)
				
				model_results[lang_code] = {
					"BLEU": bleu_score,
					"chrF": chrf_score,
					"num_examples": len(source_texts),
					"translation_time": translation_time,
					"translations_file": str(translations_file)
				}
				
				print(f"{lang_code} Results:")
				print(f"BLEU: {bleu_score:.2f}")
				print(f"chrF: {chrf_score:.2f}")
				print(f"Translation time: {translation_time:.2f} seconds")
				
			except Exception as e:
				print(f"Error processing {lang_code}: {str(e)}")
				import traceback
				traceback.print_exc()
				model_results[lang_code] = {"error": str(e)}
		
		all_results[model_path] = model_results
		
		# Save metrics for this model
		metrics_file = model_output_dir / "metrics.json"
		with open(metrics_file, 'w') as f:
			json.dump(model_results, f, indent=2)
	
	# Save combined results
	with open(output_dir / "all_metrics.json", 'w') as f:
		json.dump(all_results, f, indent=2)
	
	print("\nEvaluation complete. Results saved in evaluation_results directory.")
	print("- Individual translations are in language-specific TSV files")
	print("- Metrics are in metrics.json files")
	print("- Combined metrics are in all_metrics.json")

if __name__ == "__main__":
	main()