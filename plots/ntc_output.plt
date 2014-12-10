
set title "TagCombine (Alpha = 0.6, Beta = 0.6): Gamma vs. recall@5"
set key off
set grid
set xlabel "Gamma"
set ylabel "recall@5"
set terminal png size 800,600
set output 'tc_gamma.png'

plot "ntc_output.tab" with linespoints pt 6 lt rgb "green"

