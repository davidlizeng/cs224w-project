
set title "Similarity Based Ranking Component: recall@5"
set key off
set logscale x 10
set format x "10^{%L}"
set mxtics 10
set grid
set xlabel "Post Length (characters)"
set ylabel "recall@5 Score"
set tics scale 2
set terminal png size 800,600
set output 'sim-50000-recall5.png'

plot "sim-50000-recall5.tab" t "recall@5" with points pt 6 lt rgb "red"

