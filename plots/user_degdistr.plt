#
# Degree Distribution: Users Network. G(83548, 124295). 12083 (0.1446) nodes with in-deg > avg deg (3.0), 7902 (0.0946) with >2*avg.deg (Mon Dec  8 22:47:55 2014)
#

set title "Degree Distribution: Users Network"
set key off
set logscale xy 10
set format x "10^{%L}"
set mxtics 10
set format y "10^{%L}"
set mytics 10
set grid
set xlabel "Degree"
set ylabel "Count"
set tics scale 2
set terminal png size 1000,800
set output 'user_degdistr.png'
plot 	"user_degdistr.tab" using 1:2 title "" with points pt 6 lt rgb "blue"
