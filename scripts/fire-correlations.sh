set -euo pipefail

a=../FIREv2.0/results/GM12878/FDR-peaks/FDR-FIRE-peaks.bed.gz
b=FIRE/results/ONT_heuristic_full/FDR-peaks/FDR-FIRE-peaks.bed.gz

zcat $a | wc -l
zcat $b | wc -l

printf "#chrom\tstart\tend\tGM12878\tGM12878_ONT\n" >"./Tables/fire-correlations.tbl"

bedops --ec -m <(zcat $a) <(zcat $b) > Tables/joint.peaks.bed 

rb bl -r Tables/joint.peaks.bed

cat Tables/joint.peaks.bed |
    bedmap --ec --echo --max --delim '\t' - <(hck -z -f 1-4 -F score ../FIREv2.0/results/GM12878/FDR-peaks/FDR.track.bed.gz ) |
    bedmap --ec --echo --max --delim '\t' - <(hck -z -f 1-4 -F score FIRE/results/ONT_heuristic_full/FDR-peaks/FDR.track.bed.gz) |
    cat \
        >>"./Tables/fire-correlations.tbl"
head ./Tables/fire-correlations.tbl

bgzip -f Tables/fire-correlations.tbl

