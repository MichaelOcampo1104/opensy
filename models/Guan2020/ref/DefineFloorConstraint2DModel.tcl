# This file will be used to define floor constraint 

set	ConstrainDOF	1;	# Nodes at same floor level have identical lateral displacement 

# Level 2 
equalDOF	121	221	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	121	32	$ConstrainDOF;	# Pier 1 to Leaning column

# puts "Floor constraint defined"