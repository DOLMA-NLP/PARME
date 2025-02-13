import json
from pathlib import Path
from typing import Dict, List, Set
import random

def read_parallel_files(source_file: Path, target_file: Path) -> List[Dict]:
	"""Read parallel files and create translation entries."""
	entries = []
	seen_pairs = set()
	
	with open(source_file, 'r', encoding='utf-8') as src, \
		 open(target_file, 'r', encoding='utf-8') as tgt:
		for source_line, target_line in zip(src, tgt):
			source_text = source_line.strip()
			target_text = target_line.strip()
			
			if source_text and target_text:
				try:
					src_parts = source_text.split(' ', 1)
					tgt_parts = target_text.split(' ', 1)
					
					if len(src_parts) != 2 or len(tgt_parts) != 2:
						print(f"Skipping malformed line: {source_text} ||| {target_text}")
						continue
						
					src_lang, src_text = src_parts
					tgt_lang, tgt_text = tgt_parts
					
					pair_key = (src_text, tgt_text)
					
					if pair_key not in seen_pairs:
						seen_pairs.add(pair_key)

						entry = {
							"translation": {
								src_lang: src_text,
								tgt_lang: tgt_text
							}
						}
						entries.append(entry)
				except ValueError as e:
					print(f"Skipping malformed line: {e}")
					continue
	
	return entries

def combine_data(base_dir: str, output_dir: str, languages: List[str], val_as_train_langs: List[str]) -> tuple[str, str]:
	"""Combines data from all languages into training and validation sets."""
	output_path = Path(output_dir)
	output_path.mkdir(exist_ok=True)
	
	all_train_data = []
	all_val_data = []
	unique_pairs = set()
	
	base_path = Path(base_dir)
	print(f"Reading data from {base_path}")
	train_source = base_path / "train.source"
	train_target = base_path / "train.target"
	if train_source.exists() and train_target.exists():
		print("Processing training data...")
		train_entries = read_parallel_files(train_source, train_target)
		for entry in train_entries:
			pair_key = (
				tuple(entry["translation"].items())[0],
				tuple(entry["translation"].items())[1]
			)
			if pair_key not in unique_pairs:
				unique_pairs.add(pair_key)
				all_train_data.append(entry)
	val_source = base_path / "val.source"
	val_target = base_path / "val.target"
	if val_source.exists() and val_target.exists():
		print("Processing validation data...")
		val_entries = read_parallel_files(val_source, val_target)
		for entry in val_entries:
			src_lang = list(entry["translation"].keys())[0]
			pair_key = (
				tuple(entry["translation"].items())[0],
				tuple(entry["translation"].items())[1]
			)
			if pair_key not in unique_pairs:
				unique_pairs.add(pair_key)
				if src_lang in val_as_train_langs:
					all_train_data.append(entry)
				else:
					all_val_data.append(entry)
	random.seed(42)
	random.shuffle(all_train_data)
	random.shuffle(all_val_data)
	
	for entry in all_train_data[:2]:
		print(json.dumps(entry, indent=2, ensure_ascii=False))
		trans = entry["translation"]
		assert len(trans) == 2, f"Entry has wrong number of languages: {len(trans)}"
		for lang, text in trans.items():
			assert isinstance(text, str), f"Text is not string: {type(text)}"
			assert text is not None, f"Text is None for language {lang}"
	train_file = output_path / "train.jsonl"
	val_file = output_path / "val.jsonl"
	
	with open(train_file, 'w', encoding='utf-8') as f:
		for entry in all_train_data:
			json.dump(entry, f, ensure_ascii=False)
			f.write('\n')
	
	with open(val_file, 'w', encoding='utf-8') as f:
		for entry in all_val_data:
			json.dump(entry, f, ensure_ascii=False)
			f.write('\n')
	
	print(f"\nFiles created:")
	print(f"Train: {train_file} ({len(all_train_data)} examples)")
	print(f"Validation: {val_file} ({len(all_val_data)} examples)")
	
	return str(train_file), str(val_file)

def main():
	BASE_DIR = "../fine-tune"
	LANGUAGES = [
		"glk_Arab", "hac_Arab", "lki_Arab", "mzn_Arab", 
		"sdh_Arab", "zza_Latn", "bqi_Arab", "tly_Arab"
	]
	
	VAL_AS_TRAIN = ["bqi_Arab", "tly_Arab"]
	print("\nProcessing base setup...")
	train_file, val_file = combine_data(
		base_dir=f"{BASE_DIR}/base",
		output_dir=f"{BASE_DIR}/base",
		languages=LANGUAGES,
		val_as_train_langs=VAL_AS_TRAIN
	)
	print("\nProcessing augmented setup...")
	train_file, val_file = combine_data(
		base_dir=f"{BASE_DIR}/augmented",
		output_dir=f"{BASE_DIR}/augmented",
		languages=LANGUAGES,
		val_as_train_langs=VAL_AS_TRAIN
	)

if __name__ == "__main__":
	main()