
set title "Similarity Based Ranking Component: recall@10"
set key off
set logscale x 10
set format x "10^{%L}"
set mxtics 10
set grid
set xlabel "Post Length (characters)"
set ylabel "recall@5 Score"
set terminal png size 800,600
set output 'sim-50000-recall10.png'

plot "sim-50000-recall10.tab" t "recall@10" with points pt 6 lt rgb "red"

