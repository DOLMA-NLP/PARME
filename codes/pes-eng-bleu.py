from sacrebleu.metrics import BLEU, CHRF

def evaluate_translations(hypotheses, references):
	"""Calculate BLEU and chrF scores"""
	bleu = BLEU()
	chrf = CHRF()
	
	bleu_score = bleu.corpus_score(hypotheses, [references])
	chrf_score = chrf.corpus_score(hypotheses, [references])
	
	return bleu_score.score, chrf_score.score

datasets = {
	"BQI": {"val": "datasets/BQI-val.tsv"},
	"GLK": {"train": "datasets/GLK-train.tsv", "val": "datasets/GLK-val.tsv"},
	"HAC": {"train": "datasets/HAC-train.tsv", "val": "datasets/HAC-val.tsv"},
	"LKI": {"train": "datasets/LKI-train.tsv", "val": "datasets/LKI-val.tsv"},
	"MZN": {"train": "datasets/MZN-train.tsv", "val": "datasets/MZN-val.tsv"},
	"SDH": {"train": "datasets/SDH-train.tsv", "val": "datasets/SDH-val.tsv"},
	"TLY": {"val": "datasets/TLY-val.tsv"},
	"ZZA": {"train": "datasets/ZZA-train.tsv", "val": "datasets/ZZA-val.tsv"}
}

with open("datasets/zza-kmr_gtrans_translated.tsv", "r") as f:
	kmr_eng = {i.split("\t")[0]: i.split("\t")[1] for i in f.read().splitlines()[1:]}

with open("datasets/pes_sentences_nllb_600M_translated.tsv", "r") as f:
	pes_eng = {i.split("\t")[0]: i.split("\t")[1] for i in f.read().splitlines()[1:]}


for language in datasets:
	new_ref_1, ref_2_trans = list(), list()
	for split in datasets[language]:
		with open(datasets[language][split], "r") as f:
			dataset = f.read().splitlines()[1:]
		
		ref_1 = [i.split("\t")[0] for i in dataset] # English column
		ref_2 = [i.split("\t")[1] for i in dataset] # other reference (Farsi or Kurmanji)
		
		for eng, i in zip(ref_1, ref_2):
			if language != "ZZA":
				if i in pes_eng:
					new_ref_1.append(eng)
					ref_2_trans.append(pes_eng[i])
			else:
				if i in kmr_eng:
					new_ref_1.append(eng)
					ref_2_trans.append(kmr_eng[i])
	
	bleu_score, chrf_score = evaluate_translations(ref_2_trans, new_ref_1)
	print(language, bleu_score, chrf_score)




