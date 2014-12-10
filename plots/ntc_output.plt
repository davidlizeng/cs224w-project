
set title "NetTagCombine (Alpha = 0.4, Beta = 0.4, Gamma = 1.0): Delta vs. recall@5"
set key off
set grid
set xlabel "Delta"
set ylabel "recall@5"
set terminal png size 800,600
set output 'ntc_delta.png'

plot "ntc_output.tab" with linespoints pt 6 lt rgb "orange"

