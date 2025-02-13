import json
import random
import os
from pathlib import Path
from collections import defaultdict

def read_jsonl_file(file_path):
	"""Read JSONL file and return list of translations."""
	data = []
	with open(file_path, 'r', encoding='utf-8') as f:
		for line in f:
			if line.strip():
				data.append(json.loads(line))
	return data

def organize_by_language(train_files, val_files):
	"""Organize translations by source language and split."""
	train_data = defaultdict(list)
	val_data = defaultdict(list)
	
	for file_path in train_files:
		data = read_jsonl_file(file_path)
		for item in data:
			src_lang = [lang for lang in item['translation'].keys() if lang != 'eng_Latn'][0]
			train_data[src_lang].append(item)
	
	for file_path in val_files:
		data = read_jsonl_file(file_path)
		for item in data:
			src_lang = [lang for lang in item['translation'].keys() if lang != 'eng_Latn'][0]
			val_data[src_lang].append(item)
	
	return train_data, val_data

def save_jsonl(data, file_path):
	"""Save data to JSONL file."""
	with open(file_path, 'w', encoding='utf-8') as f:
		for item in data:
			f.write(json.dumps(item, ensure_ascii=False) + '\n')

def create_incremental_samples(base_path):
	"""Create incrementally growing samples."""
	
	train_files = [
		'/home/user/ahmadi/DOLMA/fine-tune/base/train.jsonl',
		'/home/user/ahmadi/DOLMA/fine-tune/augmented/train.jsonl'
	]
	val_files = [
		'/home/user/ahmadi/DOLMA/fine-tune/base/val.jsonl',
		'/home/user/ahmadi/DOLMA/fine-tune/augmented/val.jsonl'
	]
	
	train_data, val_data = organize_by_language(train_files, val_files)
	
	current_train_samples = []
	current_val_samples = []
	
	for sample_num in range(1, 11):
		print(f"\nCreating sample {sample_num * 100}")
		sample_dir = Path(base_path) / str(sample_num * 100)
		sample_dir.mkdir(parents=True, exist_ok=True)
		

		new_train_samples = []
		new_val_samples = []
		
		for lang in train_data.keys():
	
			used_train = set(str(item) for item in current_train_samples)
			used_val = set(str(item) for item in current_val_samples)
			
			available_train = [s for s in train_data[lang] 
							 if str(s) not in used_train]
			available_val = [s for s in val_data[lang] 
						   if str(s) not in used_val]
			
	
			if len(available_train) >= 80:
				train_samples = random.sample(available_train, 80)
				new_train_samples.extend(train_samples)
			else:
				print(f"Warning: Only {len(available_train)} training samples available for {lang}")
				new_train_samples.extend(available_train)
			
			if len(available_val) >= 20:
				val_samples = random.sample(available_val, 20)
				new_val_samples.extend(val_samples)
			else:
				print(f"Warning: Only {len(available_val)} validation samples available for {lang}")
				new_val_samples.extend(available_val)
		

		current_train_samples.extend(new_train_samples)
		current_val_samples.extend(new_val_samples)
		

		random.shuffle(current_train_samples)
		random.shuffle(current_val_samples)
		

		save_jsonl(current_train_samples, sample_dir / 'train.jsonl')
		save_jsonl(current_val_samples, sample_dir / 'val.jsonl')
		

		train_counts = defaultdict(int)
		val_counts = defaultdict(int)
		for item in current_train_samples:
			lang = [lang for lang in item['translation'].keys() if lang != 'eng_Latn'][0]
			train_counts[lang] += 1
		for item in current_val_samples:
			lang = [lang for lang in item['translation'].keys() if lang != 'eng_Latn'][0]
			val_counts[lang] += 1
			
		print(f"Train set size: {len(current_train_samples)}")
		print(f"Val set size: {len(current_val_samples)}")
		print("Samples per language (train):", dict(train_counts))
		print("Samples per language (val):", dict(val_counts))

if __name__ == '__main__':
	random.seed(42)
	
	base_path = '/home/user/ahmadi/DOLMA/fine-tune/samples'
	# create_incremental_samples(base_path)
	print("\nIncremental sample creation completed!")
	
	# command = "python run_translation.py --model_name_or_path ./nllb_extended --do_train --do_eval --train_file /home/user/ahmadi/DOLMA/fine-tune/samples/XXX/train.jsonl --validation_file /home/user/ahmadi/DOLMA/fine-tune/samples/XXX/val.jsonl --output_dir ./nllb_finetuned_samples/nllb_finetuned_base_XXX --per_device_train_batch_size 16 --learning_rate 5e-4 --num_train_epochs 20 --warmup_ratio 0.15 --fp16 --predict_with_generate --logging_dir ./runs --logging_strategy steps --logging_steps 100 --logging_first_step --evaluation_strategy epoch --save_strategy epoch --save_total_limit 2 --metric_for_best_model eval_bleu --load_best_model_at_end --greater_is_better true --max_source_length 128 --max_target_length 128 --pad_to_max_length --num_beams 5 --weight_decay 0.01 --seed 42 --overwrite_output_dir --report_to tensorboard"
	
	# for sample_num in range(1, 11):
	# 	print(command.replace("XXX", str(sample_num * 100)))


