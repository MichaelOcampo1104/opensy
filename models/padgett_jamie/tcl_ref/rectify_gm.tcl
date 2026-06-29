#	This process is to rectify an ground motion into its x, z components so as
#	to effectively create some incident angle of loading as measured from the
#	longitudinal axis.
#     
#	Original file was created by Bryant G. Nielson
#   For details refer Nielson (2005) -  Analytical fragility curves for highway bridges in moderate seismic zones

proc rectify_gm {EQ_no  angle name} {

#set EQ_no 1
#set angle 45
#file mkdir trash
#set name "trash"
#
set file_gm1 [open [concat ground_motions/x_component/eq_x$EQ_no.acn] "r"]; # loading x component
set file_gm2 [open [concat ground_motions/y_component/eq_y$EQ_no.acn] "r"]; # loading y component

set file_gm_x [open [concat $name/gm_x.acn] "w"]; # file for rotated x-component
set file_gm_z [open [concat $name/gm_z.acn] "w"]; # file for rotated y-component

set file_gm_len [open [concat $name/gm_length.out] "w"]; # file for stroing the information on thelength of the ground motion (number of points)

set q 0
while {[gets $file_gm1 line]>=0} {
	gets $file_gm2 line2
	set q [expr $q+1]
	scan $line "%f"  gm1($q)
	scan $line2 "%f" gm2($q)
    # rotating the ground motions
	set gm_x [expr cos($angle*6.2832/360.)*$gm1($q)+cos($angle*6.2832/360. + 3.1416/2.)*$gm2($q)]
	puts $file_gm_x $gm_x ; # writing the rotated ground motion acceleration 
	set gm_z [expr sin($angle*6.2832/360.)*$gm1($q)+sin($angle*6.2832/360. + 3.1416/2.)*$gm2($q)]
	puts $file_gm_z $gm_z ; # writing the rotated ground motion acceleration 
}

puts $file_gm_len $q ; # writing the length information in to theh file

# closing open files
close $file_gm1
close $file_gm2
close $file_gm_x
close $file_gm_z
close $file_gm_len

}
