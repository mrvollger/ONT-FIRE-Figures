mkdir -p best

ls alns/*.bam \
  | parallel -n 1 \
    'best --intervals-hp -n {/.} -t 16 {} ../data/denovo-asm/GM12878.v0.1.0.scaffold.fa best/{/.}'

