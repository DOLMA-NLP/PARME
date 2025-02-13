from transformers import NllbTokenizer, M2M100ForConditionalGeneration, AutoConfig
import torch
from pathlib import Path
import os

def extend_tokenizer_and_model(model, tokenizer, new_lang_code, similar_lang_code):
	"""
	Extend NLLB tokenizer and model with new language tags
	"""
	# Add new token to tokenizer if it doesn't exist
	if new_lang_code not in tokenizer.get_vocab():
		print(f"Adding new language token: {new_lang_code}")
		num_added_tokens = tokenizer.add_tokens([new_lang_code], special_tokens=True)
		
		# Resize token embeddings
		model.resize_token_embeddings(len(tokenizer))
		
		# Get embedding of similar language
		similar_lang_embedding = model.get_input_embeddings().weight[
			tokenizer.convert_tokens_to_ids(similar_lang_code)
		].clone()
		
		# Initialize new language embedding
		with torch.no_grad():
			model.get_input_embeddings().weight[
				tokenizer.convert_tokens_to_ids(new_lang_code)
			] = similar_lang_embedding
		
		print(f"Successfully initialized {new_lang_code} with {similar_lang_code} embedding")
	else:
		print(f"Language {new_lang_code} already exists in tokenizer")

def prepare_nllb_model(model_name, new_langs, similar_langs):
	"""
	Prepare NLLB model with new language tags
	"""
	print(f"Loading model and tokenizer from {model_name}")
	
	# Load base model and tokenizer
	tokenizer = NllbTokenizer.from_pretrained(model_name)
	config = AutoConfig.from_pretrained(model_name)
	model = M2M100ForConditionalGeneration.from_pretrained(model_name, config=config)
	
	# Add new languages
	for new_lang, similar_lang in zip(new_langs, similar_langs):
		extend_tokenizer_and_model(model, tokenizer, new_lang, similar_lang)
	
	return model, tokenizer

def main():
	# New languages and their similar languages for initialization
	language_pairs = {
		'sdh_Arab': 'ckb_Arab',
		'zza_Latn': 'kmr_Latn',
		'hac_Arab': 'ckb_Arab',
		'lki_Arab': 'ckb_Arab',
		'glk_Arab': 'pes_Arab',
		'mzn_Arab': 'pes_Arab',
		'bqi_Arab': 'pes_Arab',
		'tly_Arab': 'pes_Arab'
	}
	
	# Base paths
	model_name = "facebook/nllb-200-distilled-600M"
	output_dir = Path("nllb_extended")
	
	# Prepare model
	print("Starting model preparation...")
	model, tokenizer = prepare_nllb_model(
		model_name, 
		list(language_pairs.keys()), 
		list(language_pairs.values())
	)
	
	# Save the modified model and tokenizer
	print(f"Saving extended model and tokenizer to {output_dir}")
	os.makedirs(output_dir, exist_ok=True)
	model.save_pretrained(output_dir)
	tokenizer.save_pretrained(output_dir)
	
	print("Model extension completed successfully!")

if __name__ == "__main__":
	main()