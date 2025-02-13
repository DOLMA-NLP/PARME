import json
import os
from pathlib import Path

def read_jsonl_file(file_path):
	"""Read JSONL file and return list of translations."""
	data = []
	with open(file_path, 'r', encoding='utf-8') as f:
		for line in f:
			if line.strip():
				data.append(json.loads(line))
	return data

def save_jsonl(data, file_path):
	"""Save data to JSONL file."""
	with open(file_path, 'w', encoding='utf-8') as f:
		for item in data:
			f.write(json.dumps(item, ensure_ascii=False) + '\n')

def create_ablation_samples():
	"""Create ablation samples by removing one language at a time from 1000-sample dataset."""
	
	base_train = read_jsonl_file('/home/user/ahmadi/DOLMA/fine-tune/samples/1000/train.jsonl')
	base_val = read_jsonl_file('/home/user/ahmadi/DOLMA/fine-tune/samples/1000/val.jsonl')
	
	languages_to_ablate = [
		'bqi_Arab',
		'lki_Arab',
		'mzn_Arab',
		'hac_Arab',
		'glk_Arab',
		'zza_Latn',
		'sdh_Arab',
		'tly_Arab'
	]
	
	for ablated_lang in languages_to_ablate:
		print(f"\nCreating ablation sample without {ablated_lang}")
		

		sample_dir = Path(f'/home/user/ahmadi/DOLMA/fine-tune/ablation/1000-{ablated_lang.split("_")[0]}')
		sample_dir.mkdir(parents=True, exist_ok=True)
		

		ablated_train = [item for item in base_train 
						if ablated_lang not in item['translation'].keys()]
		ablated_val = [item for item in base_val 
					  if ablated_lang not in item['translation'].keys()]
		

		save_jsonl(ablated_train, sample_dir / 'train.jsonl')
		save_jsonl(ablated_val, sample_dir / 'val.jsonl')
		

		train_counts = {}
		val_counts = {}
		for item in ablated_train:
			lang = [lang for lang in item['translation'].keys() if lang != 'eng_Latn'][0]
			train_counts[lang] = train_counts.get(lang, 0) + 1
		for item in ablated_val:
			lang = [lang for lang in item['translation'].keys() if lang != 'eng_Latn'][0]
			val_counts[lang] = val_counts.get(lang, 0) + 1
			
		print(f"Train set size: {len(ablated_train)}")
		print(f"Val set size: {len(ablated_val)}")
		print("Samples per language (train):", train_counts)
		print("Samples per language (val):", val_counts)

if __name__ == '__main__':
	create_ablation_samples()
	print("\nAblation sample creation completed!")


	# command = "python run_translation.py --model_name_or_path ./nllb_extended --do_train --do_eval --train_file /home/user/ahmadi/DOLMA/fine-tune/ablation/1000-XXX/train.jsonl --validation_file /home/user/ahmadi/DOLMA/fine-tune/ablation/1000-XXX/val.jsonl --output_dir ./nllb-finetuned_ablation/nllb_finetuned_base_XXX --per_device_train_batch_size 16 --learning_rate 5e-4 --num_train_epochs 20 --warmup_ratio 0.15 --fp16 --predict_with_generate --logging_dir ./runs --logging_strategy steps --logging_steps 100 --logging_first_step --evaluation_strategy epoch --save_strategy epoch --save_total_limit 2 --metric_for_best_model eval_bleu --load_best_model_at_end --greater_is_better true --max_source_length 128 --max_target_length 128 --pad_to_max_length --num_beams 5 --weight_decay 0.01 --seed 42 --overwrite_output_dir --report_to tensorboard"
	
	# for language in ['bqi', 'lki', 'mzn', 'hac', 'glk', 'zza', 'sdh', 'tly']:
	# 	print(command.replace("XXX", language))