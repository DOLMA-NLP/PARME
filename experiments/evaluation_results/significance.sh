# 1. To compare each m_aug to corresponding m_base of the same config:

# Config I
sacrebleu base_merged.ref -i base_merged.hyp augmented_merged.hyp --paired-bs --paired-bs-n 1000

# Config II
sacrebleu base_merged.ref -i base_II_merged.hyp augmented_II_merged.hyp --paired-bs --paired-bs-n 1000

# Config III
sacrebleu base_merged.ref -i base_III_merged.hyp augmented_III_merged.hyp --paired-bs --paired-bs-n 1000

# Config II+
sacrebleu base_merged.ref -i base_II_merged.hyp base_II_improved_merged.hyp --paired-bs --paired-bs-n 1000


# 2. To compare Config III to Config I:

# Compare base systems
sacrebleu base_merged.ref -i base_merged.hyp base_III_merged.hyp --paired-bs --paired-bs-n 1000

# Compare augmented systems
sacrebleu base_merged.ref -i augmented_merged.hyp augmented_III_merged.hyp --paired-bs --paired-bs-n 1000


# 3. To compare Config II to Config I and then to Config III:

# Config II vs Config I (base)
sacrebleu base_merged.ref -i base_merged.hyp base_II_merged.hyp --paired-bs --paired-bs-n 1000

# Config II vs Config I (augmented)
sacrebleu base_merged.ref -i augmented_merged.hyp augmented_II_merged.hyp --paired-bs --paired-bs-n 1000

# Config II vs Config III (base)
sacrebleu base_merged.ref -i base_III_merged.hyp base_II_merged.hyp --paired-bs --paired-bs-n 1000

# Config II vs Config III (augmented)
sacrebleu base_merged.ref -i augmented_III_merged.hyp augmented_II_merged.hyp --paired-bs --paired-bs-n 1000


# 4. To compare Config II+ to Config II:
sacrebleu base_merged.ref -i base_II_merged.hyp base_II_improved_merged.hyp --paired-bs --paired-bs-n 1000

