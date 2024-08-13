# split the sdh corpus into smaller batches of 1000 lines
split -l 1000 sdh_sentences.txt output_ && i=1; for f in output_*; do mv "$f" "$(printf "SDH-F-%02d.tsv" $i)"; i=$((i + 1)); done

split -l 1000 random_sample_20k.txt output_ && i=1; for f in output_*; do mv "$f" "$(printf "random_20k-%02d.tsv" $i)"; i=$((i + 1)); done