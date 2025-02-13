import json
import re
from sacrebleu.metrics import BLEU, CHRF, TER
bleu = BLEU()
chrf = CHRF()

datasets = {
	"BQI-arab": "DOLMA/evaluation/outputs/BQI-arab_results.json",
	"GLK-arab": "DOLMA/evaluation/outputs/GLK-arab_results.json",
	"HAC-arab": "DOLMA/evaluation/outputs/HAC-arab_results.json",
	"LKI-arab": "DOLMA/evaluation/outputs/LKI-arab_results.json",
	"MZN-arab": "DOLMA/evaluation/outputs/MZN-arab_results.json",
	"SDH-arab": "DOLMA/evaluation/outputs/SDH-arab_results.json",
	"TLY-arab": "DOLMA/evaluation/outputs/TLY-arab_results.json",
	"ZZA-latn": "DOLMA/evaluation/outputs/ZZA-latn_results.json",
	"BQI-latn": "DOLMA/evaluation/outputs/BQI-latn_results.json",
	"GLK-latn": "DOLMA/evaluation/outputs/GLK-latn_results.json",
	"HAC-latn": "DOLMA/evaluation/outputs/HAC-latn_results.json",
	"LKI-latn": "DOLMA/evaluation/outputs/LKI-latn_results.json",
	"MZN-latn": "DOLMA/evaluation/outputs/MZN-latn_results.json",
	"SDH-latn": "DOLMA/evaluation/outputs/SDH-latn_results.json",
	"TLY-latn": "DOLMA/evaluation/outputs/TLY-latn_results.json",
	"ZZA-arab": "DOLMA/evaluation/outputs/ZZA-arab_results.json",
}

datasets_3_3 = {
	"BQI-arab": "DOLMA/evaluation/outputs_3.3/BQI-arab_results.json",
	"GLK-arab": "DOLMA/evaluation/outputs_3.3/GLK-arab_results.json",
	"HAC-arab": "DOLMA/evaluation/outputs_3.3/HAC-arab_results.json",
	"LKI-arab": "DOLMA/evaluation/outputs_3.3/LKI-arab_results.json",
	"MZN-arab": "DOLMA/evaluation/outputs_3.3/MZN-arab_results.json",
	"SDH-arab": "DOLMA/evaluation/outputs_3.3/SDH-arab_results.json",
	"TLY-arab": "DOLMA/evaluation/outputs_3.3/TLY-arab_results.json",
	"ZZA-latn": "DOLMA/evaluation/outputs_3.3/ZZA-latn_results.json",
}

datasets = datasets_3_3

for lang_code in datasets:
	result_bleu, result_chrf = "", ""
	print("\nProcessing %s..."%lang_code)
	with open(datasets[lang_code], 'r') as f:
		data = json.load(f)
	
	print("=== BLEU Scores ===")
	for source_lang in ["arb_Latn", "eng_Latn", "tur_Latn", "kmr_Latn", "pes_Arab", "ckb_Arab", "arb_Arab"]:
		for target_lang in ["eng_Latn"]:#, "pes_Arab"]:
			if len(data["translations"][source_lang][target_lang]):
				sys = data["translations"][source_lang][target_lang]
				ref = [data["source_en"]]
				
				bleu_score = bleu.corpus_score(sys, ref)
				bleu_value = float(re.search(r'BLEU = (\d+\.\d+)', str(bleu_score)).group(1))
				print("Source: %s, Target: Eng >>> %s"%(source_lang, bleu_value))
	
	print("\n=== CHrF Scores ===")
	for source_lang in ["arb_Latn", "eng_Latn", "tur_Latn", "kmr_Latn", "pes_Arab", "ckb_Arab", "arb_Arab"]:
		for target_lang in ["eng_Latn"]:#, "pes_Arab"]:
			if len(data["translations"][source_lang][target_lang]):
				sys = data["translations"][source_lang][target_lang]
				ref = [data["source_en"]]

				chrf_score = chrf.corpus_score(sys, ref)
				chrf_value = float(re.search(r'chrF2 = (\d+\.\d+)', str(chrf_score)).group(1))

				print("Source: %s, Target: Eng >>> %s"%(source_lang, chrf_value))
