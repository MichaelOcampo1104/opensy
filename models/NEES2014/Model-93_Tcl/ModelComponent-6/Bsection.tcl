proc Bsection {secID matID D t nfdw nftw nfbf nftf} {
	# #########################################################
	# creates an standard equal side box section
	# input parameters
	# secID - section ID number
	# matID - material ID number 
	# D  = Section depth
	# t  = Section thikness
	# nfdw = number of fibers along wall (web) depth 
	# nftw = number of fibers along wall thickness
	# nfbf = number of fibers along flange width
	# nftf = number of fibers along flange thickness
  	
	set dw [expr $D-2*$t]

	set y1 [expr -$D/2]
	set y2 [expr -$dw/2]
	set y3 [expr  $dw/2]
	set y4 [expr  $D/2]

	set z1 $y1
	set z2 $y2
	set z3 $y3
	set z4 $y4

	section fiberSec  $secID  {
   		#                     nfIJ  nfJK    yI  zI    yJ  zJ    yK  zK    yL  zL
   		patch quadr  $matID  $nfbf $nftf   $y1 $z4   $y1 $z1   $y2 $z1   $y2 $z4;	#bot flange
   		patch quadr  $matID  $nfbf $nftf   $y3 $z4   $y3 $z1   $y4 $z1   $y4 $z4;	#top flange
   		patch quadr  $matID  $nftw $nfdw   $y2 $z1   $y3 $z1   $y3 $z2   $y2 $z2;	#right wall
   		patch quadr  $matID  $nftw $nfdw   $y2 $z4   $y2 $z3   $y3 $z3   $y3 $z4;	#left  wall
	}
}