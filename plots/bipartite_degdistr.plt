
set title "Degree Distribution of # Tags Associated per User (first 50k Questions)"
set key off
set logscale xy 10
set format xy "10^{%L}"
set mxtics 10
set mytics 10
set grid
set xlabel "# Tags (Degree)"
set ylabel "Frequency"
set terminal png size 800,600
set output 'bipartite_degdistr.png'

plot "bipartite_degdistr.tab" with points pt 6 lt rgb "red"

