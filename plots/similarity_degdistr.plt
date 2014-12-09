#
# Degree Distribution: Post Similarity. G(50000, 1704460). 8279 (0.1656) nodes with in-deg > avg deg (68.2), 3138 (0.0628) with >2*avg.deg (Mon Dec  8 21:54:25 2014)
#

set title "Degree Distribution: Post Similarity"
set key off
set logscale xy 10
set format x "10^{%L}"
set mxtics 10
set format y "10^{%L}"
set mytics 10
set grid
set xlabel "In-degree"
set ylabel "Count"
set tics scale 2
set terminal png size 1000,800
set output 'similarity_degdistr.png'
plot "similarity_degdistr.tab" with points pt 6 lt rgb "green"
