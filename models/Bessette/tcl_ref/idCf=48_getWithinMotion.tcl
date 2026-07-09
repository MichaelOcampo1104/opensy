###################################################################################################
# JP3 Parametric Study - Phase 1 - SSC Site Response Analysis with Elastic Half-space
# 
# AnalysisID: "ModelConfig_id48_SSC_SRA WithinMotion"
# 
# Model Config. id: 48
# 
# Ground Motion ids: [234 84 41 142 124 8 35 72 111 135 135]
# 
# copyright: Caroline Bessette, University of Colorado Boulder, 04/17/2024 00:22
###################################################################################################
#--------------------------------------------------------------------------------------------------
#          00 - Set Up & Source Definition
#--------------------------------------------------------------------------------------------------

wipe
set startTime [clock clicks -milliseconds]

# Ground motion information
set matGMid {234 84 41 142 124 8 35 72 111 135 149 0}
set matGMDT {0.005 0.005 0.005 0.005 0.005 0.005 0.005 0.01 0.005 0.005 0.004 0}
set matGMdur {185 185 185 185 185 185 185 185 185 185 185 0}
set matGMdur1 {45 43 51 24 75 43 43 40 79 58 32 0}
set matGMdur2 {140 142 134 161 110 142 142 145 106 127 153 0}

for {set index 1} {$index < [llength $matGMid]} {incr index} {
	set idgmi $index
	puts "idgmi: $idgmi"
	puts "idgm: [lindex $matGMid $index-1]"
	set fileORID [concat "vel_idgm[lindex $matGMid $idgmi-1]"]
	puts "fileORID: $fileORID"
	set fileWMID [concat "acc_idgm[lindex $matGMid $idgmi-1]_0"]
	puts "fileWMID: $fileWMID"
	set mpcorec [concat "SSC_WM_idgm[lindex $matGMid $idgmi-1]"]

	#--------------------------------------------------------------------------------------------------
	#          1 - DEFINE NODES
	#--------------------------------------------------------------------------------------------------

	# Soil Nodes
	model basic -ndm 3 -ndf 4
	# tag x y z
	node 1 0 1 16.5
	node 2 0 0 16.5
	node 3 1 0 16.5
	node 4 1 1 16.5
	node 5 0 1 17.5
	node 6 0 0 17.5
	node 7 1 0 17.5
	node 8 1 1 17.5
	node 21 0 1 15.5
	node 22 0 0 15.5
	node 23 1 0 15.5
	node 24 1 1 15.5
	node 33 0 1 15
	node 34 0 0 15
	node 35 1 0 15
	node 36 1 1 15
	node 45 0 1 14.5
	node 46 0 0 14.5
	node 47 1 0 14.5
	node 48 1 1 14.5
	node 57 0 1 13.5
	node 58 0 0 13.5
	node 59 1 0 13.5
	node 60 1 1 13.5
	node 69 0 1 12.5
	node 70 0 0 12.5
	node 71 1 0 12.5
	node 72 1 1 12.5
	node 81 0 1 11.5
	node 82 0 0 11.5
	node 83 1 0 11.5
	node 84 1 1 11.5
	node 93 0 1 10.5
	node 94 0 0 10.5
	node 95 1 0 10.5
	node 96 1 1 10.5
	node 105 0 1 9.5
	node 106 0 0 9.5
	node 107 1 0 9.5
	node 108 1 1 9.5
	node 117 0 1 8.75
	node 118 0 0 8.75
	node 119 1 0 8.75
	node 120 1 1 8.75
	node 129 0 1 7.857
	node 130 0 0 7.857
	node 131 1 0 7.857
	node 132 1 1 7.857
	node 141 0 1 6.964
	node 142 0 0 6.964
	node 143 1 0 6.964
	node 144 1 1 6.964
	node 153 0 1 6.071
	node 154 0 0 6.071
	node 155 1 0 6.071
	node 156 1 1 6.071
	node 165 0 1 5.179
	node 166 0 0 5.179
	node 167 1 0 5.179
	node 168 1 1 5.179
	node 177 0 1 4.286
	node 178 0 0 4.286
	node 179 1 0 4.286
	node 180 1 1 4.286
	node 189 0 1 3.393
	node 190 0 0 3.393
	node 191 1 0 3.393
	node 192 1 1 3.393
	node 201 0 1 2.5
	node 202 0 0 2.5
	node 203 1 0 2.5
	node 204 1 1 2.5
	node 213 0 1 2
	node 214 0 0 2
	node 215 1 0 2
	node 216 1 1 2
	node 225 0 1 1
	node 226 0 0 1
	node 227 1 0 1
	node 228 1 1 1
	node 237 0 1 0
	node 238 0 0 0
	node 239 1 0 0
	node 240 1 1 0

	model basic -ndm 3 -ndf 3
	# tag x y z
	node 9 0 0.5 16.5
	node 10 0.5 0 16.5
	node 11 1 0.5 16.5
	node 12 0.5 1 16.5
	node 13 0 0.5 17.5
	node 14 0.5 0 17.5
	node 15 1 0.5 17.5
	node 16 0.5 1 17.5
	node 17 0 1 17
	node 18 0 0 17
	node 19 1 0 17
	node 20 1 1 17
	node 25 0 0.5 15.5
	node 26 0.5 0 15.5
	node 27 1 0.5 15.5
	node 28 0.5 1 15.5
	node 29 0 1 16
	node 30 0 0 16
	node 31 1 0 16
	node 32 1 1 16
	node 37 0 0.5 15
	node 38 0.5 0 15
	node 39 1 0.5 15
	node 40 0.5 1 15
	node 41 0 1 15.25
	node 42 0 0 15.25
	node 43 1 0 15.25
	node 44 1 1 15.25
	node 49 0 0.5 14.5
	node 50 0.5 0 14.5
	node 51 1 0.5 14.5
	node 52 0.5 1 14.5
	node 53 0 1 14.75
	node 54 0 0 14.75
	node 55 1 0 14.75
	node 56 1 1 14.75
	node 61 0 0.5 13.5
	node 62 0.5 0 13.5
	node 63 1 0.5 13.5
	node 64 0.5 1 13.5
	node 65 0 1 14
	node 66 0 0 14
	node 67 1 0 14
	node 68 1 1 14
	node 73 0 0.5 12.5
	node 74 0.5 0 12.5
	node 75 1 0.5 12.5
	node 76 0.5 1 12.5
	node 77 0 1 13
	node 78 0 0 13
	node 79 1 0 13
	node 80 1 1 13
	node 85 0 0.5 11.5
	node 86 0.5 0 11.5
	node 87 1 0.5 11.5
	node 88 0.5 1 11.5
	node 89 0 1 12
	node 90 0 0 12
	node 91 1 0 12
	node 92 1 1 12
	node 97 0 0.5 10.5
	node 98 0.5 0 10.5
	node 99 1 0.5 10.5
	node 100 0.5 1 10.5
	node 101 0 1 11
	node 102 0 0 11
	node 103 1 0 11
	node 104 1 1 11
	node 109 0 0.5 9.5
	node 110 0.5 0 9.5
	node 111 1 0.5 9.5
	node 112 0.5 1 9.5
	node 113 0 1 10
	node 114 0 0 10
	node 115 1 0 10
	node 116 1 1 10
	node 121 0 0.5 8.75
	node 122 0.5 0 8.75
	node 123 1 0.5 8.75
	node 124 0.5 1 8.75
	node 125 0 1 9.125
	node 126 0 0 9.125
	node 127 1 0 9.125
	node 128 1 1 9.125
	node 133 0 0.5 7.857
	node 134 0.5 0 7.857
	node 135 1 0.5 7.857
	node 136 0.5 1 7.857
	node 137 0 1 8.304
	node 138 0 0 8.304
	node 139 1 0 8.304
	node 140 1 1 8.304
	node 145 0 0.5 6.964
	node 146 0.5 0 6.964
	node 147 1 0.5 6.964
	node 148 0.5 1 6.964
	node 149 0 1 7.411
	node 150 0 0 7.411
	node 151 1 0 7.411
	node 152 1 1 7.411
	node 157 0 0.5 6.071
	node 158 0.5 0 6.071
	node 159 1 0.5 6.071
	node 160 0.5 1 6.071
	node 161 0 1 6.518
	node 162 0 0 6.518
	node 163 1 0 6.518
	node 164 1 1 6.518
	node 169 0 0.5 5.179
	node 170 0.5 0 5.179
	node 171 1 0.5 5.179
	node 172 0.5 1 5.179
	node 173 0 1 5.625
	node 174 0 0 5.625
	node 175 1 0 5.625
	node 176 1 1 5.625
	node 181 0 0.5 4.286
	node 182 0.5 0 4.286
	node 183 1 0.5 4.286
	node 184 0.5 1 4.286
	node 185 0 1 4.732
	node 186 0 0 4.732
	node 187 1 0 4.732
	node 188 1 1 4.732
	node 193 0 0.5 3.393
	node 194 0.5 0 3.393
	node 195 1 0.5 3.393
	node 196 0.5 1 3.393
	node 197 0 1 3.839
	node 198 0 0 3.839
	node 199 1 0 3.839
	node 200 1 1 3.839
	node 205 0 0.5 2.5
	node 206 0.5 0 2.5
	node 207 1 0.5 2.5
	node 208 0.5 1 2.5
	node 209 0 1 2.946
	node 210 0 0 2.946
	node 211 1 0 2.946
	node 212 1 1 2.946
	node 217 0 0.5 2
	node 218 0.5 0 2
	node 219 1 0.5 2
	node 220 0.5 1 2
	node 221 0 1 2.25
	node 222 0 0 2.25
	node 223 1 0 2.25
	node 224 1 1 2.25
	node 229 0 0.5 1
	node 230 0.5 0 1
	node 231 1 0.5 1
	node 232 0.5 1 1
	node 233 0 1 1.5
	node 234 0 0 1.5
	node 235 1 0 1.5
	node 236 1 1 1.5
	node 241 0 0.5 0
	node 242 0.5 0 0
	node 243 1 0.5 0
	node 244 0.5 1 0
	node 245 0 1 0.5
	node 246 0 0 0.5
	node 247 1 0 0.5
	node 248 1 1 0.5

	puts "Finished creating all soil nodes..."

	#--------------------------------------------------------------------------------------------------
	#          2 - MATERIALS
	#--------------------------------------------------------------------------------------------------

	# Ottawa Sand Material - Saturated
	nDMaterial PressureDependMultiYield02 30 3 1.92 78000.0 203410.0 30.0 0.1 101.0 0.5 26.0 0.75 1.61 0.01 0.21 20 2.4 3.0 1.0 0.0 0.733 0.9 0.02 0.7 101.0 0.1 0.0 1.0
	nDMaterial PressureDependMultiYield02 40 3 1.94 82000.0 213843.0 31.0 0.1 101.0 0.5 26.8 0.61 2.24 0.097 0.27 20 3.8 3.0 1.0 0.0 0.675 0.9 0.02 0.7 101.0 0.1 0.0 1.0
	nDMaterial PressureDependMultiYield02 50 3 1.96 85500.0 222970.0 32.0 0.1 101.0 0.5 29.5 0.48 2.87 0.89 0.33 20 3.8 3.0 1.0 0.0 0.675 0.9 0.02 0.7 101.0 0.1 0.0 1.0
	nDMaterial PressureDependMultiYield02 60 3 1.98 90000.0 234702.0 33.6 0.1 101.0 0.5 31.0 0.34 3.5 1.69 0.39 20 4.5 3.0 1.0 0.0 0.646 0.9 0.02 0.7 101.0 0.1 0.0 1.0
	nDMaterial PressureDependMultiYield02 70 3 1.99 94000.0 1.8727e+05 36.25 0.1 101.0 0.5 33.7 0.21 4.14 2.48 0.45 20 5.2 3.0 1.0 0.0 0.617 0.9 0.02 0.7 101.0 0.1 0.0 1.0
	nDMaterial PressureDependMultiYield02 80 3 2.01 99500.0 1.9823e+05 37.325 0.1 101.0 0.5 33.85 0.145 2.77 1.8 0.75 20 3.18 3.0 1.0 0.0 0.588 0.9 0.02 0.7 101.0 0.1 0.0 1.0
	nDMaterial PressureDependMultiYield02 90 3 2.03 105000.0 209186.0 38.5 0.1 101.0 0.5 34.0 0.076 1.36 1.12 1.05 20 1.25 3.0 1.0 0.0 0.55 0.9 0.02 0.7 101.0 0.1 0.0 1.0

	# Ottawa Sand Material - Dry
	nDMaterial PressureDependMultiYield02 31 3 1.53 78000.0 203410.0 30.0 0.1 101.0 0.5 26.0 0.75 1.61 0.01 0.21 20 2.4 3.0 1.0 0.0 0.733 0.9 0.02 0.7 101.0 2.0 0.0 1.0
	nDMaterial PressureDependMultiYield02 41 3 1.56 82000.0 213843.0 31.0 0.1 101.0 0.5 26.8 0.61 2.24 0.097 0.27 20 3.8 3.0 1.0 0.0 0.675 0.9 0.02 0.7 101.0 2.0 0.0 1.0
	nDMaterial PressureDependMultiYield02 51 3 1.58 85500.0 222970.0 32.0 0.1 101.0 0.5 29.5 0.48 2.87 0.89 0.33 20 3.8 3.0 1.0 0.0 0.675 0.9 0.02 0.7 101.0 2.0 0.0 1.0
	nDMaterial PressureDependMultiYield02 61 3 1.60 90000.0 234702.0 33.6 0.1 101.0 0.5 31.0 0.34 3.5 1.69 0.39 20 4.5 3.0 1.0 0.0 0.646 0.9 0.02 0.7 101.0 2.0 0.0 1.0
	nDMaterial PressureDependMultiYield02 71 3 1.64 94000.0 1.8727e+05 36.25 0.1 101.0 0.5 33.7 0.21 4.14 2.48 0.45 20 5.2 3.0 1.0 0.0 0.617 0.9 0.02 0.7 101.0 2.0 0.0 1.0
	nDMaterial PressureDependMultiYield02 81 3 1.67 99500.0 1.9823e+05 37.325 0.1 101.0 0.5 33.85 0.145 2.77 1.8 0.75 20 3.18 3.0 1.0 0.0 0.588 0.9 0.02 0.7 101.0 2.0 0.0 1.0
	nDMaterial PressureDependMultiYield02 91 3 1.70 105000.0 209186.0 38.5 0.1 101.0 0.5 34.0 0.076 1.36 1.12 1.05 20 1.25 3.0 1.0 0.0 0.55 0.9 0.02 0.7 101.0 2.0 0.0 1.0

	# Monterey Sand Material - Sat/Dry
	nDMaterial PressureDependMultiYield02 10 3 2.02 133000.0 260000.0 42.0 0.1 101.0 0.5 32.0 0.014 0.15 0.36 0.005 20 2.0 3.0 1.0 0.0 0.56 0.9 0.02 0.7 101.0 0.1 0.0 1.0
	nDMaterial PressureDependMultiYield02 11 3 1.68 133000.0 260000.0 42.0 0.1 101.0 0.5 32.0 0.014 0.15 0.36 0.005 20 2.0 3.0 1.0 0.0 0.56 0.9 0.02 0.7 101.0 2.0 0.0 1.0

	# Silica silt Material - Sat/Dry
	nDMaterial PressureDependMultiYield02 20 3 2.02 87600.0 233800.0 41.0 0.1 101.0 0.5 36.0 0.3 0.15 0.02 0.0 20 5.0 3.0 1.0 0.0 0.88 0.9 0.02 0.7 101.0 0.1 0.0 1.0
	nDMaterial PressureDependMultiYield02 21 3 1.41 87600.0 233800.0 41.0 0.1 101.0 0.5 36.0 0.3 0.15 0.02 0.0 20 5.0 3.0 1.0 0.0 0.88 0.9 0.02 0.7 101.0 2.0 0.0 1.0

	# Stiff clay - Sat/Dry
	nDMaterial PressureIndependMultiYield 104 3 1.80 150000 750000 75 0.1 0 80 0 20

	# Medium clay - Sat/Dry
	nDMaterial PressureIndependMultiYield 105 3 1.5 60000 300000 37 0.1 0 80 0 20

	puts "Finished creating all soil materials..."

	#--------------------------------------------------------------------------------------------------
	#          3 - ELEMENTS
	#--------------------------------------------------------------------------------------------------

	# Soil Elements
	model basic -ndm 3 -ndf 4
	# up_elements 20_8_BrickUP
	element 20_8_BrickUP 1 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 11 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 2 21 22 23 24 1 2 3 4 25 26 27 28 9 10 11 12 29 30 31 32 71 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 3 33 34 35 36 21 22 23 24 37 38 39 40 25 26 27 28 41 42 43 44 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 4 45 46 47 48 33 34 35 36 49 50 51 52 37 38 39 40 53 54 55 56 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 5 57 58 59 60 45 46 47 48 61 62 63 64 49 50 51 52 65 66 67 68 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 6 69 70 71 72 57 58 59 60 73 74 75 76 61 62 63 64 77 78 79 80 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 7 81 82 83 84 69 70 71 72 85 86 87 88 73 74 75 76 89 90 91 92 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 8 93 94 95 96 81 82 83 84 97 98 99 100 85 86 87 88 101 102 103 104 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 9 105 106 107 108 93 94 95 96 109 110 111 112 97 98 99 100 113 114 115 116 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 10 117 118 119 120 105 106 107 108 121 122 123 124 109 110 111 112 125 126 127 128 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 11 129 130 131 132 117 118 119 120 133 134 135 136 121 122 123 124 137 138 139 140 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 12 141 142 143 144 129 130 131 132 145 146 147 148 133 134 135 136 149 150 151 152 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 13 153 154 155 156 141 142 143 144 157 158 159 160 145 146 147 148 161 162 163 164 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 14 165 166 167 168 153 154 155 156 169 170 171 172 157 158 159 160 173 174 175 176 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 15 177 178 179 180 165 166 167 168 181 182 183 184 169 170 171 172 185 186 187 188 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 16 189 190 191 192 177 178 179 180 193 194 195 196 181 182 183 184 197 198 199 200 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 17 201 202 203 204 189 190 191 192 205 206 207 208 193 194 195 196 209 210 211 212 70 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 18 213 214 215 216 201 202 203 204 217 218 219 220 205 206 207 208 221 222 223 224 20 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 19 225 226 227 228 213 214 215 216 229 230 231 232 217 218 219 220 233 234 235 236 90 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81
	element 20_8_BrickUP 20 237 238 239 240 225 226 227 228 241 242 243 244 229 230 231 232 245 246 247 248 90 2200000.0 1.0 1.0 1.0 1.0 0.0 0.0 -9.81

	puts "Finished creating all elements..."

	#--------------------------------------------------------------------------------------------------
	#          4 - LYSMER DASHPOT
	#--------------------------------------------------------------------------------------------------

	# Define dashpot nodes
	model basic -ndm 3 -ndf 3

	set dashF 249
	set dashX 250
	set dashZ 251

	node $dashF  0.0 0.0 0.0
	node $dashX  0.0 0.0 0.0
	node $dashZ  0.0 0.0 0.0

	# Define fixities for dashpot nodes
	fix $dashF  1 1 1
	fix $dashX  0 1 1
	fix $dashZ  1 1 0

	# Link dashpots with soil column
	equalDOF 238 $dashX 1
	equalDOF 238 $dashZ 3

	# Dashpot material
	set colArea 1.00
	set Vsrock 1900.00
	set Denrock 2.5
	set dashpotCoeff 4750.0000

	uniaxialMaterial Viscous 1000 4750 1

	# Dashpot elements
	element zeroLength 21 $dashF $dashX -mat 1000 -dir 1
	element zeroLength 22 $dashF $dashZ -mat 1000 -dir 3

	puts "Finished creating Lysmer dashpots..."

	#--------------------------------------------------------------------------------------------------
	#          5 -  BOUNDARY CONDITIONS
	#--------------------------------------------------------------------------------------------------

	# Soil BC
	model basic -ndm 3 -ndf 4
	# Constraints.sp fix
	fix 237 0 1 1 0
	fix 238 0 1 1 0
	fix 239 0 1 1 0
	fix 240 0 1 1 0
	fix 1 0 0 0 1
	fix 2 0 0 0 1
	fix 3 0 0 0 1
	fix 4 0 0 0 1
	fix 5 0 0 0 1
	fix 6 0 0 0 1
	fix 7 0 0 0 1
	fix 8 0 0 0 1
	fix 21 0 0 0 1
	fix 22 0 0 0 1
	fix 23 0 0 0 1
	fix 24 0 0 0 1
	fix 33 0 1 0 0
	fix 34 0 1 0 0
	fix 35 0 1 0 0
	fix 36 0 1 0 0
	fix 45 0 1 0 0
	fix 46 0 1 0 0
	fix 47 0 1 0 0
	fix 48 0 1 0 0
	fix 57 0 1 0 0
	fix 58 0 1 0 0
	fix 59 0 1 0 0
	fix 60 0 1 0 0
	fix 69 0 1 0 0
	fix 70 0 1 0 0
	fix 71 0 1 0 0
	fix 72 0 1 0 0
	fix 81 0 1 0 0
	fix 82 0 1 0 0
	fix 83 0 1 0 0
	fix 84 0 1 0 0
	fix 93 0 1 0 0
	fix 94 0 1 0 0
	fix 95 0 1 0 0
	fix 96 0 1 0 0
	fix 105 0 1 0 0
	fix 106 0 1 0 0
	fix 107 0 1 0 0
	fix 108 0 1 0 0
	fix 117 0 1 0 0
	fix 118 0 1 0 0
	fix 119 0 1 0 0
	fix 120 0 1 0 0
	fix 129 0 1 0 0
	fix 130 0 1 0 0
	fix 131 0 1 0 0
	fix 132 0 1 0 0
	fix 141 0 1 0 0
	fix 142 0 1 0 0
	fix 143 0 1 0 0
	fix 144 0 1 0 0
	fix 153 0 1 0 0
	fix 154 0 1 0 0
	fix 155 0 1 0 0
	fix 156 0 1 0 0
	fix 165 0 1 0 0
	fix 166 0 1 0 0
	fix 167 0 1 0 0
	fix 168 0 1 0 0
	fix 177 0 1 0 0
	fix 178 0 1 0 0
	fix 179 0 1 0 0
	fix 180 0 1 0 0
	fix 189 0 1 0 0
	fix 190 0 1 0 0
	fix 191 0 1 0 0
	fix 192 0 1 0 0
	fix 201 0 1 0 0
	fix 202 0 1 0 0
	fix 203 0 1 0 0
	fix 204 0 1 0 0
	fix 213 0 1 0 0
	fix 214 0 1 0 0
	fix 215 0 1 0 0
	fix 216 0 1 0 0
	fix 225 0 1 0 0
	fix 226 0 1 0 0
	fix 227 0 1 0 0
	fix 228 0 1 0 0
	fix 1 0 1 0 1
	fix 2 0 1 0 1
	fix 3 0 1 0 1
	fix 4 0 1 0 1
	fix 5 0 1 0 1
	fix 6 0 1 0 1
	fix 7 0 1 0 1
	fix 8 0 1 0 1
	fix 21 0 1 0 1
	fix 22 0 1 0 1
	fix 23 0 1 0 1
	fix 24 0 1 0 1
	model basic -ndm 3 -ndf 3
	# Constraints.sp fix
	fix 241 0 1 1
	fix 242 0 1 1
	fix 243 0 1 1
	fix 244 0 1 1
	fix 10 0 1 0
	fix 12 0 1 0
	fix 14 0 1 0
	fix 16 0 1 0
	fix 17 0 1 0
	fix 18 0 1 0
	fix 19 0 1 0
	fix 20 0 1 0
	fix 26 0 1 0
	fix 28 0 1 0
	fix 29 0 1 0
	fix 30 0 1 0
	fix 31 0 1 0
	fix 32 0 1 0
	fix 38 0 1 0
	fix 40 0 1 0
	fix 41 0 1 0
	fix 42 0 1 0
	fix 43 0 1 0
	fix 44 0 1 0
	fix 50 0 1 0
	fix 52 0 1 0
	fix 53 0 1 0
	fix 54 0 1 0
	fix 55 0 1 0
	fix 56 0 1 0
	fix 62 0 1 0
	fix 64 0 1 0
	fix 65 0 1 0
	fix 66 0 1 0
	fix 67 0 1 0
	fix 68 0 1 0
	fix 74 0 1 0
	fix 76 0 1 0
	fix 77 0 1 0
	fix 78 0 1 0
	fix 79 0 1 0
	fix 80 0 1 0
	fix 86 0 1 0
	fix 88 0 1 0
	fix 89 0 1 0
	fix 90 0 1 0
	fix 91 0 1 0
	fix 92 0 1 0
	fix 98 0 1 0
	fix 100 0 1 0
	fix 101 0 1 0
	fix 102 0 1 0
	fix 103 0 1 0
	fix 104 0 1 0
	fix 110 0 1 0
	fix 112 0 1 0
	fix 113 0 1 0
	fix 114 0 1 0
	fix 115 0 1 0
	fix 116 0 1 0
	fix 122 0 1 0
	fix 124 0 1 0
	fix 125 0 1 0
	fix 126 0 1 0
	fix 127 0 1 0
	fix 128 0 1 0
	fix 134 0 1 0
	fix 136 0 1 0
	fix 137 0 1 0
	fix 138 0 1 0
	fix 139 0 1 0
	fix 140 0 1 0
	fix 146 0 1 0
	fix 148 0 1 0
	fix 149 0 1 0
	fix 150 0 1 0
	fix 151 0 1 0
	fix 152 0 1 0
	fix 158 0 1 0
	fix 160 0 1 0
	fix 161 0 1 0
	fix 162 0 1 0
	fix 163 0 1 0
	fix 164 0 1 0
	fix 170 0 1 0
	fix 172 0 1 0
	fix 173 0 1 0
	fix 174 0 1 0
	fix 175 0 1 0
	fix 176 0 1 0
	fix 182 0 1 0
	fix 184 0 1 0
	fix 185 0 1 0
	fix 186 0 1 0
	fix 187 0 1 0
	fix 188 0 1 0
	fix 194 0 1 0
	fix 196 0 1 0
	fix 197 0 1 0
	fix 198 0 1 0
	fix 199 0 1 0
	fix 200 0 1 0
	fix 206 0 1 0
	fix 208 0 1 0
	fix 209 0 1 0
	fix 210 0 1 0
	fix 211 0 1 0
	fix 212 0 1 0
	fix 218 0 1 0
	fix 220 0 1 0
	fix 221 0 1 0
	fix 222 0 1 0
	fix 223 0 1 0
	fix 224 0 1 0
	fix 230 0 1 0
	fix 232 0 1 0
	fix 233 0 1 0
	fix 234 0 1 0
	fix 235 0 1 0
	fix 236 0 1 0
	fix 245 0 1 0
	fix 246 0 1 0
	fix 247 0 1 0
	fix 248 0 1 0
	# Constraints.mp EqualDOF
	model basic -ndm 3 -ndf 3
	# Base of the colum - x
	equalDOF 238 237 1
	equalDOF 238 239 1
	equalDOF 238 240 1
	equalDOF 238 241 1
	equalDOF 238 242 1
	equalDOF 238 243 1
	equalDOF 238 244 1

	# Soil Edge Periodic Boundaries
	equalDOF 1 4 1 2 3
	equalDOF 2 3 1 2 3
	equalDOF 5 8 1 2 3
	equalDOF 6 7 1 2 3
	equalDOF 9 11 1 2 3
	equalDOF 13 15 1 2 3
	equalDOF 17 20 1 2 3
	equalDOF 18 19 1 2 3
	equalDOF 21 24 1 2 3
	equalDOF 22 23 1 2 3
	equalDOF 25 27 1 2 3
	equalDOF 29 32 1 2 3
	equalDOF 30 31 1 2 3
	equalDOF 33 36 1 2 3
	equalDOF 34 35 1 2 3
	equalDOF 37 39 1 2 3
	equalDOF 41 44 1 2 3
	equalDOF 42 43 1 2 3
	equalDOF 45 48 1 2 3
	equalDOF 46 47 1 2 3
	equalDOF 49 51 1 2 3
	equalDOF 53 56 1 2 3
	equalDOF 54 55 1 2 3
	equalDOF 57 60 1 2 3
	equalDOF 58 59 1 2 3
	equalDOF 61 63 1 2 3
	equalDOF 65 68 1 2 3
	equalDOF 66 67 1 2 3
	equalDOF 69 72 1 2 3
	equalDOF 70 71 1 2 3
	equalDOF 73 75 1 2 3
	equalDOF 77 80 1 2 3
	equalDOF 78 79 1 2 3
	equalDOF 81 84 1 2 3
	equalDOF 82 83 1 2 3
	equalDOF 85 87 1 2 3
	equalDOF 89 92 1 2 3
	equalDOF 90 91 1 2 3
	equalDOF 93 96 1 2 3
	equalDOF 94 95 1 2 3
	equalDOF 97 99 1 2 3
	equalDOF 101 104 1 2 3
	equalDOF 102 103 1 2 3
	equalDOF 105 108 1 2 3
	equalDOF 106 107 1 2 3
	equalDOF 109 111 1 2 3
	equalDOF 113 116 1 2 3
	equalDOF 114 115 1 2 3
	equalDOF 117 120 1 2 3
	equalDOF 118 119 1 2 3
	equalDOF 121 123 1 2 3
	equalDOF 125 128 1 2 3
	equalDOF 126 127 1 2 3
	equalDOF 129 132 1 2 3
	equalDOF 130 131 1 2 3
	equalDOF 133 135 1 2 3
	equalDOF 137 140 1 2 3
	equalDOF 138 139 1 2 3
	equalDOF 141 144 1 2 3
	equalDOF 142 143 1 2 3
	equalDOF 145 147 1 2 3
	equalDOF 149 152 1 2 3
	equalDOF 150 151 1 2 3
	equalDOF 153 156 1 2 3
	equalDOF 154 155 1 2 3
	equalDOF 157 159 1 2 3
	equalDOF 161 164 1 2 3
	equalDOF 162 163 1 2 3
	equalDOF 165 168 1 2 3
	equalDOF 166 167 1 2 3
	equalDOF 169 171 1 2 3
	equalDOF 173 176 1 2 3
	equalDOF 174 175 1 2 3
	equalDOF 177 180 1 2 3
	equalDOF 178 179 1 2 3
	equalDOF 181 183 1 2 3
	equalDOF 185 188 1 2 3
	equalDOF 186 187 1 2 3
	equalDOF 189 192 1 2 3
	equalDOF 190 191 1 2 3
	equalDOF 193 195 1 2 3
	equalDOF 197 200 1 2 3
	equalDOF 198 199 1 2 3
	equalDOF 201 204 1 2 3
	equalDOF 202 203 1 2 3
	equalDOF 205 207 1 2 3
	equalDOF 209 212 1 2 3
	equalDOF 210 211 1 2 3
	equalDOF 213 216 1 2 3
	equalDOF 214 215 1 2 3
	equalDOF 217 219 1 2 3
	equalDOF 221 224 1 2 3
	equalDOF 222 223 1 2 3
	equalDOF 225 228 1 2 3
	equalDOF 226 227 1 2 3
	equalDOF 229 231 1 2 3
	equalDOF 233 236 1 2 3
	equalDOF 234 235 1 2 3
	equalDOF 237 240 1 2 3
	equalDOF 238 239 1 2 3
	equalDOF 241 243 1 2 3
	equalDOF 245 248 1 2 3
	equalDOF 246 247 1 2 3

	puts "Finished creating all soil boundary conditions..."

	#--------------------------------------------------------------------------------------------------
	#          6 - UPDATE STAGE ELASTIC
	#--------------------------------------------------------------------------------------------------

	# soil material stage : elastic
	updateMaterialStage -material 11 -stage 0
	updateMaterialStage -material 20 -stage 0
	updateMaterialStage -material 70 -stage 0
	updateMaterialStage -material 71 -stage 0
	updateMaterialStage -material 90 -stage 0

	#--------------------------------------------------------------------------------------------------
	#          7 - RAYLEIGH DAMPING - SOIL
	#--------------------------------------------------------------------------------------------------

	# Misc_commands region

	# Soil Rayleigh Damping
	set pi 3.141592654
	set damp 0.03
	set omega1 [expr 2*$pi*3.960]
	set omega2 [expr 2*$pi*19.798]
	set a0 [expr 2*$damp*$omega1*$omega2/($omega1 + $omega2)]
	set a1 [expr 2*$damp/($omega1 + $omega2)]

	region 4 \
	-eleRange 1 20 \
	-rayleigh $a0 0.0 $a1 0.0

	puts "damping coefficients: a_0 = $a0;  a_1 = $a1"

	#--------------------------------------------------------------------------------------------------
	#          8 - STAGE 1 - GRAVITY ANALYSIS ELASTIC COMMANDS
	#--------------------------------------------------------------------------------------------------

	puts ""
	puts "BEGIN STAGE 1 - ELASTIC ANALYSIS WITH SOIL SELF WEIGHT"
	# analyses command
	constraints Penalty 1e+15 1e+15
	numberer RCM
	system Mumps -ICNTL14 200
	test NormDispIncr 0.001 100 1
	algorithm KrylovNewton -iterate current
	integrator Newmark 0.50 0.25
	analysis Transient
	analyze 10 500.0

	loadConst -time 0.0

	puts "DONE STAGE 1 - ELASTIC ANALYSIS WITH SOIL SELF WEIGHT"

	# Elapsed Time
	set endTime [clock clicks -milliseconds]
	set elapsedTimeMillis [expr {$endTime - $startTime}]
	set elapsedTimeSeconds [expr {int($elapsedTimeMillis / 1000.0)}]
	set elapsedTimeMinutes [expr {int($elapsedTimeMillis / (1000.0 * 60))}]
	
	if {$elapsedTimeSeconds < 60} {
	    puts "STAGE 1 END - Elapsed time: $elapsedTimeSeconds s"
	} elseif {$elapsedTimeMinutes < 60} {
	    puts "STAGE 1 END - Elapsed time: $elapsedTimeMinutes min"
	} else {
	    set elapsedTimeHours [expr {int($elapsedTimeMinutes / 60)}]
	    puts "STAGE 1 END - Elapsed time: $elapsedTimeHours hrs"
	}

	# issue a domain change so this will be the end of stage 1
	domainChange

	#--------------------------------------------------------------------------------------------------
	#          9 - UPDATE STAGE PLASTIC
	#--------------------------------------------------------------------------------------------------

	# soil material stage : elastic
	updateMaterialStage -material 11 -stage 1
	updateMaterialStage -material 20 -stage 1
	updateMaterialStage -material 70 -stage 1
	updateMaterialStage -material 71 -stage 1
	updateMaterialStage -material 90 -stage 1

	#--------------------------------------------------------------------------------------------------
	#          8 - STAGE 1 - GRAVITY ANALYSIS PLASTIC COMMANDS
	#--------------------------------------------------------------------------------------------------

	# analyses command
	constraints Penalty 1000000000000000.0 1000000000000000.0
	numberer RCM
	system Mumps -ICNTL14 200
	test NormDispIncr 0.0005 100 1
	algorithm KrylovNewton
	integrator Newmark 0.50 0.25
	analysis Transient
	analyze 0 0.0

	puts ""
	puts "BEGIN STAGE 2 - ELASTIC ANALYSIS WITH INCREMENTALLY APPLIED STRUCTURE LOAD"
	puts ""
	puts "Reducing the time step smoothly from 500.0s to 0.005s"

	set DTSum 0.0
	set offset 0

	set DT0 500.0
	set DT1 50.0
	set NSteps 10
	set LinspaceH [expr ($DT1-$DT0)/($NSteps-1)]
	set DTPrev $DT0
	for {set i 0} {$i < [expr $NSteps-1]} {incr i; incr offset} {
	    puts "($offset) ANALYZE WITH DT = $DTPrev"
	    analyze 1 $DTPrev
	    set DTSum [expr $DTSum + $DTPrev]
	    set DTPrev [expr $DTPrev + $LinspaceH]
	}
	# up to here SumDT = 2700, end of linear time series
	# from here on the time series is constant

	set DT0 50.0
	set DT1 0.5
	set NSteps 10
	set LinspaceH [expr ($DT1-$DT0)/($NSteps-1)]
	set DTPrev $DT0
	for {set i 0} {$i < [expr $NSteps-1]} {incr i; incr offset} {
	    puts "($offset) $DTPrev"
	    analyze 1 $DTPrev
	    set DTSum [expr $DTSum + $DTPrev]
	    set DTPrev [expr $DTPrev + $LinspaceH]
	}

	set DT0 0.5
	set DT1 0.005
	set NSteps 10
	set LinspaceH [expr ($DT1-$DT0)/($NSteps-1)]
	set DTPrev $DT0
	for {set i 0} {$i < $NSteps} {incr i; incr offset} {
	    puts "($offset) $DTPrev"
	    analyze 1 $DTPrev
	    set DTSum [expr $DTSum + $DTPrev]
	    set DTPrev [expr $DTPrev + $LinspaceH]
	    if {$i == $NSteps - 2} {
	        set DTPrev $DT1
	    }
	}
	puts "Sum: $DTSum"

	# message

	puts ""
	puts "DONE STAGE 2 - ELASTIC  ANALYSIS WITH INCREMENTALLY APPLIED STRUCTURE LOAD"

	# Elapsed Time
	set endTime [clock clicks -milliseconds]
	set elapsedTimeMillis [expr {$endTime - $startTime}]
	set elapsedTimeMinutes [expr {int($elapsedTimeMillis / (1000.0 * 60))}]
	
	if {$elapsedTimeMinutes < 60} {
	    puts "STAGE 2 END - Elapsed time: $elapsedTimeMinutes min"
	} else {
	    set elapsedTimeHours [expr {int($elapsedTimeMinutes / 60)}]
	    puts "STAGE 2 END - Elapsed time: $elapsedTimeHours hrs"
	}

	#issue a domain change
	domainChange

	loadConst -time 0.0

	#--------------------------------------------------------------------------------------------------
	#          11 - UPDATE ELEMENT PERMEABILITY VALUES FOR POST-GRAVITY ANALYSIS
	#--------------------------------------------------------------------------------------------------

	# Misc_commands parameter

	# updateParameter
	set matIDk1 3.0581e-08
	set matIDk2 1.0688e-05
	set matIDk3 1.213e-05
	set matIDk4 5.4027e-05

	# set parameter
	setParameter -value $matIDk1 -ele 18 hPerm
	setParameter -value $matIDk1 -ele 18 hPerm
	setParameter -value $matIDk1 -ele 18 vPerm
	# set parameter
	setParameter -value $matIDk2 -ele 19 hPerm
	setParameter -value $matIDk2 -ele 19 hPerm
	setParameter -value $matIDk2 -ele 19 vPerm
	setParameter -value $matIDk2 -ele 20 hPerm
	setParameter -value $matIDk2 -ele 20 hPerm
	setParameter -value $matIDk2 -ele 20 vPerm
	# set parameter
	setParameter -value $matIDk3 -ele 2 hPerm
	setParameter -value $matIDk3 -ele 2 hPerm
	setParameter -value $matIDk3 -ele 2 vPerm
	setParameter -value $matIDk3 -ele 3 hPerm
	setParameter -value $matIDk3 -ele 3 hPerm
	setParameter -value $matIDk3 -ele 3 vPerm
	setParameter -value $matIDk3 -ele 4 hPerm
	setParameter -value $matIDk3 -ele 4 hPerm
	setParameter -value $matIDk3 -ele 4 vPerm
	setParameter -value $matIDk3 -ele 5 hPerm
	setParameter -value $matIDk3 -ele 5 hPerm
	setParameter -value $matIDk3 -ele 5 vPerm
	setParameter -value $matIDk3 -ele 6 hPerm
	setParameter -value $matIDk3 -ele 6 hPerm
	setParameter -value $matIDk3 -ele 6 vPerm
	setParameter -value $matIDk3 -ele 7 hPerm
	setParameter -value $matIDk3 -ele 7 hPerm
	setParameter -value $matIDk3 -ele 7 vPerm
	setParameter -value $matIDk3 -ele 8 hPerm
	setParameter -value $matIDk3 -ele 8 hPerm
	setParameter -value $matIDk3 -ele 8 vPerm
	setParameter -value $matIDk3 -ele 9 hPerm
	setParameter -value $matIDk3 -ele 9 hPerm
	setParameter -value $matIDk3 -ele 9 vPerm
	setParameter -value $matIDk3 -ele 10 hPerm
	setParameter -value $matIDk3 -ele 10 hPerm
	setParameter -value $matIDk3 -ele 10 vPerm
	setParameter -value $matIDk3 -ele 11 hPerm
	setParameter -value $matIDk3 -ele 11 hPerm
	setParameter -value $matIDk3 -ele 11 vPerm
	setParameter -value $matIDk3 -ele 12 hPerm
	setParameter -value $matIDk3 -ele 12 hPerm
	setParameter -value $matIDk3 -ele 12 vPerm
	setParameter -value $matIDk3 -ele 13 hPerm
	setParameter -value $matIDk3 -ele 13 hPerm
	setParameter -value $matIDk3 -ele 13 vPerm
	setParameter -value $matIDk3 -ele 14 hPerm
	setParameter -value $matIDk3 -ele 14 hPerm
	setParameter -value $matIDk3 -ele 14 vPerm
	setParameter -value $matIDk3 -ele 15 hPerm
	setParameter -value $matIDk3 -ele 15 hPerm
	setParameter -value $matIDk3 -ele 15 vPerm
	setParameter -value $matIDk3 -ele 16 hPerm
	setParameter -value $matIDk3 -ele 16 hPerm
	setParameter -value $matIDk3 -ele 16 vPerm
	setParameter -value $matIDk3 -ele 17 hPerm
	setParameter -value $matIDk3 -ele 17 hPerm
	setParameter -value $matIDk3 -ele 17 vPerm
	# set parameter
	setParameter -value $matIDk4 -ele 1 hPerm
	setParameter -value $matIDk4 -ele 1 hPerm
	setParameter -value $matIDk4 -ele 1 vPerm

	puts "Finished updating permeabilities for dynamic analysis..."

	#--------------------------------------------------------------------------------------------------
	#          12 - GROUND MOTION
	#--------------------------------------------------------------------------------------------------

	# define velocity time history file
	set dataDirORM OutcropMotions
	set velocityFile [concat "$fileORID.out"]

	# timeseries object for force history
	set mSeries "Path -dt [lindex $matGMDT $idgmi-1] -filePath $dataDirORM/$velocityFile -factor $dashpotCoeff"

	# loading object
	pattern Plain 10 $mSeries {
	    load 238 1.0 0.0 0.0 0.0
	}
	puts "Dynamic loading created..."

	#--------------------------------------------------------------------------------------------------
	#          13 - CREATE POST-GRAVITY RECORDERS 
	#--------------------------------------------------------------------------------------------------

	puts "Create post-gravity recorders"

	set dataDirWM WithinMotions
	eval "recorder Node -file $dataDirWM/$fileWMID.out -time -dT [lindex $matGMDT $idgmi-1] -node 239 -dof 1 accel"

	set dataDirSSC ResultsSSC
	file mkdir $dataDirSSC

	set SSCEPInodes {	3 	7 	23 	35 	47 	59 	71 	83 	95 	107 	119 	131 	143 	155 	167 	179 	191 	203 	215 	227 	239	}
	eval "recorder Node -file $dataDirSSC/SSCEPI_pwp_idCf48_GM[lindex $matGMid $idgmi-1].out -time -dT 0.005 -node $SSCEPInodes -dof 4 vel"

	eval "recorder Node -file $dataDirSSC/SSC_acc_idCf48_GM[lindex $matGMid $idgmi-1].out -time -dT 0.005 -node $SSCEPInodes -dof 1 accel"

	#--------------------------------------------------------------------------------------------------
	#          14 - STAGE 3 - DYNAMIC ANALYSIS
	#--------------------------------------------------------------------------------------------------

	# analyses command
	constraints Penalty 1000000000000000.0 1000000000000000.0
	numberer RCM
	system Mumps -ICNTL14 200
	test NormDispIncr 1.0e-3 50 0
	algorithm KrylovNewton -iterate current
	integrator Newmark 0.50 0.25
	analysis Transient

	# RUN Non-linear Analysis with timestep reduction loop
	set nSteps [expr int([lindex $matGMdur $idgmi-1]/[lindex $matGMDT $idgmi-1])]
	set ok [analyze $nSteps [lindex $matGMDT $idgmi-1]]

	set dT [lindex $matGMDT $idgmi-1]

	# if analysis fails, reduce timestep and continue with analysis
	if {$ok != 0} {
		puts "did not converge, reducing time step"
		set curTime  [getTime]
		set mTime $curTime
		puts "curTime: $curTime"
		set curStep  [expr $curTime/$dT]
		puts "curStep: $curStep"
		set rStep  [expr ($nSteps-$curStep)*2.0]
		set remStep  [expr int(($nSteps-$curStep)*2.0)]
		puts "remStep: $remStep"
		set dT       [expr $dT/2.0]
		puts "dT: $dT"
		set ok [analyze  $remStep  $dT]
		# if analysis fails again, reduce timestep and continue with analysis
		if {$ok != 0} {
			puts "did not converge, reducing time step"
			set curTime  [getTime]
			puts "curTime: $curTime"
			set curStep  [expr ($curTime-$mTime)/$dT]
			puts "curStep: $curStep"
			set remStep  [expr int(($rStep-$curStep)*2.0)]
			puts "remStep: $remStep"
			set dT       [expr $dT/2.0]
			puts "dT: $dT"
			analyze  $remStep  $dT
		}
	}

	# Reset time and analysis
	loadConst 0.0
	setTime 0.0
	wipeAnalysis
	remove recorders

	wipe
	# --------------------------------------------------------------------------------------------------
}
