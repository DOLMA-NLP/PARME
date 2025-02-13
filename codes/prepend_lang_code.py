import json

folder_dir = "/home/user/ahmadi/DOLMA/fine-tune/"
files = ["base/train.jsonl", "base/val.jsonl", "augmented/train.jsonl", "augmented/val.jsonl"]
for file in files:
	data, new_data = list(), list()
	with open(folder_dir + file, "r") as f:
		for line in f:
			data.append(json.loads(line))

	for line in data:
		new_line = dict()
		for i in line["translation"].keys():
			new_line.update({i: i + " " + line["translation"][i]})
		new_data.append({"translation": new_line})

	with open(folder_dir + file.replace(".jsonl", "_prefixed.jsonl"), 'w', encoding='utf-8') as f:
		for entry in new_data:
			json.dump(entry, f, ensure_ascii=False)
			f.write('\n')