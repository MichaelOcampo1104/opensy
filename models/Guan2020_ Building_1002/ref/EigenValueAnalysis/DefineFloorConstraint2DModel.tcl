# This file will be used to define floor constraint 
# Nodes at same floor level have identical lateral displacement
# Select mid right node of each panel zone as the constrained node

set	ConstrainDOF	1;  # X-direction

# Level 2 
equalDOF	1211	2211	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	1211	3211	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	1211	4211	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	1211	52	$ConstrainDOF;	#Pier 1 to Leaning column

# Level 3 
equalDOF	1311	2311	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	1311	3311	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	1311	4311	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	1311	53	$ConstrainDOF;	#Pier 1 to Leaning column

# Level 4 
equalDOF	1411	2411	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	1411	3411	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	1411	4411	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	1411	54	$ConstrainDOF;	#Pier 1 to Leaning column

# Level 5 
equalDOF	1511	2511	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	1511	3511	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	1511	4511	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	1511	55	$ConstrainDOF;	#Pier 1 to Leaning column

# Level 6 
equalDOF	1611	2611	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	1611	3611	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	1611	4611	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	1611	56	$ConstrainDOF;	#Pier 1 to Leaning column

# Level 7 
equalDOF	1711	2711	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	1711	3711	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	1711	4711	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	1711	57	$ConstrainDOF;	#Pier 1 to Leaning column

# Level 8 
equalDOF	1811	2811	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	1811	3811	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	1811	4811	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	1811	58	$ConstrainDOF;	#Pier 1 to Leaning column

# Level 9 
equalDOF	1911	2911	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	1911	3911	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	1911	4911	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	1911	59	$ConstrainDOF;	#Pier 1 to Leaning column

# Level 10 
equalDOF	11011	21011	$ConstrainDOF;	# Pier 1 to Pier 2
equalDOF	11011	31011	$ConstrainDOF;	# Pier 1 to Pier 3
equalDOF	11011	41011	$ConstrainDOF;	# Pier 1 to Pier 4
equalDOF	11011	510	$ConstrainDOF;	#Pier 1 to Leaning column

puts "Floor constraint defined"