
# truss_elements truss
element truss 1 6 7 1.0 82
element truss 2 7 8 1.0 85
element truss 3 7 9 1.0 72
element truss 4 7 10 1.0 72
element truss 5 7 11 1.0 72
element truss 6 11 12 1.0 72
element truss 7 12 13 1.0 72
element truss 8 13 14 1.0 72
element truss 9 10 15 1.0 72
element truss 10 11 16 1.0 72
element truss 11 15 11 1.0 72
element truss 12 13 17 1.0 72
element truss 13 16 13 1.0 72
element truss 14 18 15 1.0 72
element truss 15 15 19 1.0 72
element truss 16 16 20 1.0 72
element truss 17 19 16 1.0 72
element truss 18 20 17 1.0 72


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 19)
node 255 4000 200 4800
rigidLink beam 150 255

# Extra nodes for zeroLength
# node tag x y z
node 256 4000 200 4800
node 257 4000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 19 0.0 -0.0 1.0
element elasticBeamColumn 19 256 257 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 19

# zero_length_elements zeroLength
element zeroLength 840 255 256 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 841 257 20 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 20)
node 258 7800 5500 4800
rigidLink beam 151 258

# Extra nodes for zeroLength
# node tag x y z
node 259 4000 5500 4800
node 260 7800 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 20 0.0 0.0 1.0
element elasticBeamColumn 20 259 260 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 20

# zero_length_elements zeroLength
element zeroLength 842 20 259 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 843 260 258 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 21)
node 261 8000 5700 4800
rigidLink beam 151 261


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 17), with Mesh Node = 23 (auxiliary for element 21)
node 262 8000 8800 4800
rigidLink beam 152 262

# Extra nodes for zeroLength
# node tag x y z
node 263 8000 5700 4800
node 264 8000 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 21 0.0 -0.0 1.0
element elasticBeamColumn 21 263 264 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 21

# zero_length_elements zeroLength
element zeroLength 844 261 263 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 845 264 262 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 22)
node 265 8200 5500 4800
rigidLink beam 151 265

# Extra nodes for zeroLength
# node tag x y z
node 266 8200 5500 4800
node 267 12000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 22 0.0 0.0 1.0
element elasticBeamColumn 22 266 267 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 22

# zero_length_elements zeroLength
element zeroLength 846 265 266 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 847 267 19 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 23)
node 268 8000 5500 5000
rigidLink beam 22 268
# Geometric transformation command
geomTransf PDelta 23 1.0 0.0 -0.0
element forceBeamColumn 23 268 16 23 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 24)
node 269 4000 5500 7900
rigidLink beam 24 269
# Geometric transformation command
geomTransf PDelta 24 1.0 0.0 -0.0
element forceBeamColumn 24 20 269 24 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 25)
node 270 4000 5500 8300
rigidLink beam 24 270
# Geometric transformation command
geomTransf PDelta 25 1.0 0.0 -0.0
element forceBeamColumn 25 270 13 25 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 26)
node 271 8000 8800 8100
rigidLink beam 154 271

# Extra nodes for zeroLength
# node tag x y z
node 272 8000 5500 8100
node 273 8000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 26 0.0 -0.0 1.0
element elasticBeamColumn 26 272 273 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 26

# zero_length_elements zeroLength
element zeroLength 848 16 272 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 849 273 271 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 27)
node 274 4200 5500 8100
rigidLink beam 153 274

# Extra nodes for zeroLength
# node tag x y z
node 275 4200 5500 8100
node 276 8000 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 27 0.0 0.0 1.0
element elasticBeamColumn 27 275 276 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 27

# zero_length_elements zeroLength
element zeroLength 850 274 275 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 851 276 16 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 28)
node 277 11800 5500 8100
rigidLink beam 155 277

# Extra nodes for zeroLength
# node tag x y z
node 278 8000 5500 8100
node 279 11800 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 28 0.0 0.0 1.0
element elasticBeamColumn 28 278 279 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 28

# zero_length_elements zeroLength
element zeroLength 852 16 278 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 853 279 277 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 29)
node 280 8000 9200 8100
rigidLink beam 154 280


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 29)
node 281 8000 14300 8100
rigidLink beam 156 281

# Extra nodes for zeroLength
# node tag x y z
node 282 8000 9200 8100
node 283 8000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 29 0.0 -0.0 1.0
element elasticBeamColumn 29 282 283 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 29

# zero_length_elements zeroLength
element zeroLength 854 280 282 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 855 283 281 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 30)
node 284 12000 5700 8100
rigidLink beam 155 284


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 30)
node 285 12000 8800 8100
rigidLink beam 157 285

# Extra nodes for zeroLength
# node tag x y z
node 286 12000 5700 8100
node 287 12000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 30 0.0 -0.0 1.0
element elasticBeamColumn 30 286 287 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 30

# zero_length_elements zeroLength
element zeroLength 856 284 286 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 857 287 285 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 31)
node 288 4000 200 8100
rigidLink beam 158 288


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 31)
node 289 4000 5300 8100
rigidLink beam 153 289

# Extra nodes for zeroLength
# node tag x y z
node 290 4000 200 8100
node 291 4000 5300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 31 0.0 -0.0 1.0
element elasticBeamColumn 31 290 291 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 31

# zero_length_elements zeroLength
element zeroLength 858 288 290 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 859 291 289 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 32)
node 292 8000 200 8100
rigidLink beam 159 292

# Extra nodes for zeroLength
# node tag x y z
node 293 8000 200 8100
node 294 8000 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 32 0.0 -0.0 1.0
element elasticBeamColumn 32 293 294 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 32

# zero_length_elements zeroLength
element zeroLength 860 292 293 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 861 294 16 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 33)
node 295 12000 200 8100
rigidLink beam 160 295


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 33)
node 296 12000 5300 8100
rigidLink beam 155 296

# Extra nodes for zeroLength
# node tag x y z
node 297 12000 200 8100
node 298 12000 5300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 33 0.0 -0.0 1.0
element elasticBeamColumn 33 297 298 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 33

# zero_length_elements zeroLength
element zeroLength 862 295 297 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 863 298 296 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 26), with Mesh Node = 32 (auxiliary for element 34)
node 299 4000 5500 14500
rigidLink beam 32 299
# Geometric transformation command
geomTransf PDelta 34 1.0 0.0 -0.0
element forceBeamColumn 34 13 299 34 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 35)
node 300 12000 9000 8300
rigidLink beam 28 300


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 35)
node 301 12000 9000 11200
rigidLink beam 33 301
# Geometric transformation command
geomTransf PDelta 35 1.0 0.0 -0.0
element forceBeamColumn 35 300 301 35 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 36)
node 302 12000 9200 11400
rigidLink beam 162 302


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 36)
node 303 12000 14300 11400
rigidLink beam 163 303

# Extra nodes for zeroLength
# node tag x y z
node 304 12000 9200 11400
node 305 12000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 36 0.0 -0.0 1.0
element elasticBeamColumn 36 304 305 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 36

# zero_length_elements zeroLength
element zeroLength 864 302 304 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 865 305 303 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 17), with Mesh Node = 23 (auxiliary for element 37)
node 306 8000 9000 4600
rigidLink beam 23 306
# Geometric transformation command
geomTransf PDelta 37 1.0 0.0 -0.0
element forceBeamColumn 37 35 306 37 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 38)
node 307 4000 0 4600
rigidLink beam 21 307
# Geometric transformation command
geomTransf PDelta 38 1.0 0.0 -0.0
element forceBeamColumn 38 36 307 38 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 31), with Mesh Node = 37 (auxiliary for element 39)
node 308 200 0 4800
rigidLink beam 164 308


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 39)
node 309 3800 0 4800
rigidLink beam 150 309

# Extra nodes for zeroLength
# node tag x y z
node 310 200 0 4800
node 311 3800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 39 0.0 0.0 1.0
element elasticBeamColumn 39 310 311 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 39

# zero_length_elements zeroLength
element zeroLength 866 308 310 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 867 311 309 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 40)
node 312 4000 8800 4800
rigidLink beam 165 312

# Extra nodes for zeroLength
# node tag x y z
node 313 4000 5500 4800
node 314 4000 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 40 0.0 -0.0 1.0
element elasticBeamColumn 40 313 314 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 40

# zero_length_elements zeroLength
element zeroLength 868 20 313 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 869 314 312 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 31), with Mesh Node = 37 (auxiliary for element 41)
node 315 0 200 4800
rigidLink beam 164 315


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 33), with Mesh Node = 39 (auxiliary for element 41)
node 316 0 5300 4800
rigidLink beam 166 316

# Extra nodes for zeroLength
# node tag x y z
node 317 0 200 4800
node 318 0 5300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 41 0.0 -0.0 1.0
element elasticBeamColumn 41 317 318 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 41

# zero_length_elements zeroLength
element zeroLength 870 315 317 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 871 318 316 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 42)
node 319 4200 0 4800
rigidLink beam 150 319


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 34), with Mesh Node = 40 (auxiliary for element 42)
node 320 7800 0 4800
rigidLink beam 167 320

# Extra nodes for zeroLength
# node tag x y z
node 321 4200 0 4800
node 322 7800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 42 0.0 0.0 1.0
element elasticBeamColumn 42 321 322 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 42

# zero_length_elements zeroLength
element zeroLength 872 319 321 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 873 322 320 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 34), with Mesh Node = 40 (auxiliary for element 43)
node 323 8200 0 4800
rigidLink beam 167 323


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 35), with Mesh Node = 41 (auxiliary for element 43)
node 324 11800 0 4800
rigidLink beam 168 324

# Extra nodes for zeroLength
# node tag x y z
node 325 8200 0 4800
node 326 11800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 43 0.0 0.0 1.0
element elasticBeamColumn 43 325 326 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 43

# zero_length_elements zeroLength
element zeroLength 874 323 325 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 875 326 324 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 33), with Mesh Node = 39 (auxiliary for element 44)
node 327 200 5500 4800
rigidLink beam 166 327

# Extra nodes for zeroLength
# node tag x y z
node 328 200 5500 4800
node 329 4000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 44 0.0 0.0 1.0
element elasticBeamColumn 44 328 329 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 44

# zero_length_elements zeroLength
element zeroLength 876 327 328 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 877 329 20 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 35), with Mesh Node = 41 (auxiliary for element 45)
node 330 12200 0 4800
rigidLink beam 168 330


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 36), with Mesh Node = 42 (auxiliary for element 45)
node 331 15800 0 4800
rigidLink beam 169 331

# Extra nodes for zeroLength
# node tag x y z
node 332 12200 0 4800
node 333 15800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 45 0.0 0.0 1.0
element elasticBeamColumn 45 332 333 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 45

# zero_length_elements zeroLength
element zeroLength 878 330 332 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 879 333 331 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 46)
node 334 4000 9000 5000
rigidLink beam 38 334


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 37), with Mesh Node = 43 (auxiliary for element 46)
node 335 4000 9000 7900
rigidLink beam 43 335
# Geometric transformation command
geomTransf PDelta 46 1.0 0.0 -0.0
element forceBeamColumn 46 334 335 46 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 37), with Mesh Node = 43 (auxiliary for element 47)
node 336 4000 9000 8300
rigidLink beam 43 336


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 38), with Mesh Node = 44 (auxiliary for element 47)
node 337 4000 9000 11200
rigidLink beam 44 337
# Geometric transformation command
geomTransf PDelta 47 1.0 0.0 -0.0
element forceBeamColumn 47 336 337 47 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 39), with Mesh Node = 45 (auxiliary for element 48)
node 338 200 5500 11400
rigidLink beam 172 338

# Extra nodes for zeroLength
# node tag x y z
node 339 200 5500 11400
node 340 4000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 48 0.0 0.0 1.0
element elasticBeamColumn 48 339 340 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 48

# zero_length_elements zeroLength
element zeroLength 880 338 339 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 881 340 13 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 49)
node 341 4200 9000 4800
rigidLink beam 165 341


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 17), with Mesh Node = 23 (auxiliary for element 49)
node 342 7800 9000 4800
rigidLink beam 152 342

# Extra nodes for zeroLength
# node tag x y z
node 343 4200 9000 4800
node 344 7800 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 49 0.0 0.0 1.0
element elasticBeamColumn 49 343 344 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 49

# zero_length_elements zeroLength
element zeroLength 882 341 343 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 883 344 342 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 38), with Mesh Node = 44 (auxiliary for element 50)
node 345 4200 9000 11400
rigidLink beam 171 345


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 40), with Mesh Node = 46 (auxiliary for element 50)
node 346 7800 9000 11400
rigidLink beam 173 346

# Extra nodes for zeroLength
# node tag x y z
node 347 4200 9000 11400
node 348 7800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 50 0.0 0.0 1.0
element elasticBeamColumn 50 347 348 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 50

# zero_length_elements zeroLength
element zeroLength 884 345 347 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 885 348 346 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 38), with Mesh Node = 44 (auxiliary for element 51)
node 349 4000 8800 11400
rigidLink beam 171 349

# Extra nodes for zeroLength
# node tag x y z
node 350 4000 5500 11400
node 351 4000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 51 0.0 -0.0 1.0
element elasticBeamColumn 51 350 351 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 51

# zero_length_elements zeroLength
element zeroLength 886 13 350 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 887 351 349 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 35), with Mesh Node = 41 (auxiliary for element 52)
node 352 12000 0 5000
rigidLink beam 41 352


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 52)
node 353 12000 0 7900
rigidLink beam 31 353
# Geometric transformation command
geomTransf PDelta 52 1.0 0.0 -0.0
element forceBeamColumn 52 352 353 52 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 36), with Mesh Node = 42 (auxiliary for element 53)
node 354 16000 0 5000
rigidLink beam 42 354


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 53)
node 355 16000 0 7900
rigidLink beam 47 355
# Geometric transformation command
geomTransf PDelta 53 1.0 0.0 -0.0
element forceBeamColumn 53 354 355 53 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 54)
node 356 4200 14500 8100
rigidLink beam 175 356


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 54)
node 357 7800 14500 8100
rigidLink beam 156 357

# Extra nodes for zeroLength
# node tag x y z
node 358 4200 14500 8100
node 359 7800 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 54 0.0 0.0 1.0
element elasticBeamColumn 54 358 359 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 54

# zero_length_elements zeroLength
element zeroLength 888 356 358 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 889 359 357 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 37), with Mesh Node = 43 (auxiliary for element 55)
node 360 4000 9200 8100
rigidLink beam 170 360


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 55)
node 361 4000 14300 8100
rigidLink beam 175 361

# Extra nodes for zeroLength
# node tag x y z
node 362 4000 9200 8100
node 363 4000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 55 0.0 -0.0 1.0
element elasticBeamColumn 55 362 363 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 55

# zero_length_elements zeroLength
element zeroLength 890 360 362 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 891 363 361 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 37), with Mesh Node = 43 (auxiliary for element 56)
node 364 4200 9000 8100
rigidLink beam 170 364


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 56)
node 365 7800 9000 8100
rigidLink beam 154 365

# Extra nodes for zeroLength
# node tag x y z
node 366 4200 9000 8100
node 367 7800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 56 0.0 0.0 1.0
element elasticBeamColumn 56 366 367 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 56

# zero_length_elements zeroLength
element zeroLength 892 364 366 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 893 367 365 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 43), with Mesh Node = 49 (auxiliary for element 57)
node 368 200 9000 8100
rigidLink beam 176 368


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 37), with Mesh Node = 43 (auxiliary for element 57)
node 369 3800 9000 8100
rigidLink beam 170 369

# Extra nodes for zeroLength
# node tag x y z
node 370 200 9000 8100
node 371 3800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 57 0.0 0.0 1.0
element elasticBeamColumn 57 370 371 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 57

# zero_length_elements zeroLength
element zeroLength 894 368 370 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 895 371 369 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 58)
node 372 3800 14500 8100
rigidLink beam 175 372


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 44), with Mesh Node = 50 (auxiliary for element 58)
node 373 200 14500 8100
rigidLink beam 177 373

# Extra nodes for zeroLength
# node tag x y z
node 374 3800 14500 8100
node 375 200 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 58 0.0 0.0 1.0
element elasticBeamColumn 58 374 375 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 58

# zero_length_elements zeroLength
element zeroLength 896 372 374 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 897 375 373 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 45), with Mesh Node = 51 (auxiliary for element 59)
node 376 200 0 8100
rigidLink beam 178 376


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 59)
node 377 3800 0 8100
rigidLink beam 158 377

# Extra nodes for zeroLength
# node tag x y z
node 378 200 0 8100
node 379 3800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 59 0.0 0.0 1.0
element elasticBeamColumn 59 378 379 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 59

# zero_length_elements zeroLength
element zeroLength 898 376 378 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 899 379 377 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 60)
node 380 0 9000 5000
rigidLink beam 52 380


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 43), with Mesh Node = 49 (auxiliary for element 60)
node 381 0 9000 7900
rigidLink beam 49 381
# Geometric transformation command
geomTransf PDelta 60 1.0 0.0 -0.0
element forceBeamColumn 60 380 381 60 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 61)
node 382 3800 5500 8100
rigidLink beam 153 382

# Extra nodes for zeroLength
# node tag x y z
node 383 0 5500 8100
node 384 3800 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 61 0.0 0.0 1.0
element elasticBeamColumn 61 383 384 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 61

# zero_length_elements zeroLength
element zeroLength 900 17 383 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 901 384 382 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 43), with Mesh Node = 49 (auxiliary for element 62)
node 385 0 9200 8100
rigidLink beam 176 385


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 44), with Mesh Node = 50 (auxiliary for element 62)
node 386 0 14300 8100
rigidLink beam 177 386

# Extra nodes for zeroLength
# node tag x y z
node 387 0 9200 8100
node 388 0 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 62 0.0 -0.0 1.0
element elasticBeamColumn 62 387 388 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 62

# zero_length_elements zeroLength
element zeroLength 902 385 387 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 903 388 386 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 63)
node 389 4000 5700 8100
rigidLink beam 153 389


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 37), with Mesh Node = 43 (auxiliary for element 63)
node 390 4000 8800 8100
rigidLink beam 170 390

# Extra nodes for zeroLength
# node tag x y z
node 391 4000 5700 8100
node 392 4000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 63 0.0 -0.0 1.0
element elasticBeamColumn 63 391 392 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 63

# zero_length_elements zeroLength
element zeroLength 904 389 391 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 905 392 390 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 64)
node 393 0 14500 5000
rigidLink beam 53 393


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 44), with Mesh Node = 50 (auxiliary for element 64)
node 394 0 14500 7900
rigidLink beam 50 394
# Geometric transformation command
geomTransf PDelta 64 1.0 0.0 -0.0
element forceBeamColumn 64 393 394 64 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 44), with Mesh Node = 50 (auxiliary for element 65)
node 395 0 14500 8300
rigidLink beam 50 395


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 48), with Mesh Node = 54 (auxiliary for element 65)
node 396 0 14500 11200
rigidLink beam 54 396
# Geometric transformation command
geomTransf PDelta 65 1.0 0.0 -0.0
element forceBeamColumn 65 395 396 65 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 66)
node 397 4000 0 8300
rigidLink beam 29 397


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 66)
node 398 4000 0 11200
rigidLink beam 55 398
# Geometric transformation command
geomTransf PDelta 66 1.0 0.0 -0.0
element forceBeamColumn 66 397 398 66 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 67)
node 399 4000 0 5000
rigidLink beam 21 399


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 67)
node 400 4000 0 7900
rigidLink beam 29 400
# Geometric transformation command
geomTransf PDelta 67 1.0 0.0 -0.0
element forceBeamColumn 67 399 400 67 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 34), with Mesh Node = 40 (auxiliary for element 68)
node 401 8000 0 5000
rigidLink beam 40 401


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 68)
node 402 8000 0 7900
rigidLink beam 30 402
# Geometric transformation command
geomTransf PDelta 68 1.0 0.0 -0.0
element forceBeamColumn 68 401 402 68 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 69)
node 403 12000 0 8300
rigidLink beam 31 403


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 69)
node 404 12000 0 11200
rigidLink beam 56 404
# Geometric transformation command
geomTransf PDelta 69 1.0 0.0 -0.0
element forceBeamColumn 69 403 404 69 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 70)
node 405 12200 14500 11400
rigidLink beam 163 405


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 51), with Mesh Node = 57 (auxiliary for element 70)
node 406 15800 14500 11400
rigidLink beam 184 406

# Extra nodes for zeroLength
# node tag x y z
node 407 12200 14500 11400
node 408 15800 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 70 0.0 0.0 1.0
element elasticBeamColumn 70 407 408 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 70

# zero_length_elements zeroLength
element zeroLength 906 405 407 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 907 408 406 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 71)
node 409 8000 5700 11400
rigidLink beam 185 409


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 40), with Mesh Node = 46 (auxiliary for element 71)
node 410 8000 8800 11400
rigidLink beam 173 410

# Extra nodes for zeroLength
# node tag x y z
node 411 8000 5700 11400
node 412 8000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 71 0.0 -0.0 1.0
element elasticBeamColumn 71 411 412 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 71

# zero_length_elements zeroLength
element zeroLength 908 409 411 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 909 412 410 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 72)
node 413 16000 0 8300
rigidLink beam 47 413


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 53), with Mesh Node = 59 (auxiliary for element 72)
node 414 16000 0 11200
rigidLink beam 59 414
# Geometric transformation command
geomTransf PDelta 72 1.0 0.0 -0.0
element forceBeamColumn 72 413 414 72 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 73)
node 415 12200 9000 11400
rigidLink beam 162 415


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 73)
node 416 15800 9000 11400
rigidLink beam 187 416

# Extra nodes for zeroLength
# node tag x y z
node 417 12200 9000 11400
node 418 15800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 73 0.0 0.0 1.0
element elasticBeamColumn 73 417 418 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 73

# zero_length_elements zeroLength
element zeroLength 910 415 417 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 911 418 416 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 74)
node 419 7800 5500 11400
rigidLink beam 185 419

# Extra nodes for zeroLength
# node tag x y z
node 420 4000 5500 11400
node 421 7800 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 74 0.0 0.0 1.0
element elasticBeamColumn 74 420 421 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 74

# zero_length_elements zeroLength
element zeroLength 912 13 420 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 913 421 419 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 40), with Mesh Node = 46 (auxiliary for element 75)
node 422 8200 9000 11400
rigidLink beam 173 422


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 75)
node 423 11800 9000 11400
rigidLink beam 162 423

# Extra nodes for zeroLength
# node tag x y z
node 424 8200 9000 11400
node 425 11800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 75 0.0 0.0 1.0
element elasticBeamColumn 75 424 425 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 75

# zero_length_elements zeroLength
element zeroLength 914 422 424 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 915 425 423 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 40), with Mesh Node = 46 (auxiliary for element 76)
node 426 8000 9200 11400
rigidLink beam 173 426


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 76)
node 427 8000 14300 11400
rigidLink beam 188 427

# Extra nodes for zeroLength
# node tag x y z
node 428 8000 9200 11400
node 429 8000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 76 0.0 -0.0 1.0
element elasticBeamColumn 76 428 429 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 76

# zero_length_elements zeroLength
element zeroLength 916 426 428 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 917 429 427 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 77)
node 430 4200 0 11400
rigidLink beam 182 430


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 77)
node 431 7800 0 11400
rigidLink beam 189 431

# Extra nodes for zeroLength
# node tag x y z
node 432 4200 0 11400
node 433 7800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 77 0.0 0.0 1.0
element elasticBeamColumn 77 432 433 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 77

# zero_length_elements zeroLength
element zeroLength 918 430 432 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 919 433 431 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 78)
node 434 4000 200 11400
rigidLink beam 182 434

# Extra nodes for zeroLength
# node tag x y z
node 435 4000 200 11400
node 436 4000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 78 0.0 -0.0 1.0
element elasticBeamColumn 78 435 436 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 78

# zero_length_elements zeroLength
element zeroLength 920 434 435 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 921 436 13 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 26), with Mesh Node = 32 (auxiliary for element 79)
node 437 4200 5500 14700
rigidLink beam 161 437

# Extra nodes for zeroLength
# node tag x y z
node 438 4200 5500 14700
node 439 8000 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 79 0.0 0.0 1.0
element elasticBeamColumn 79 438 439 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 79

# zero_length_elements zeroLength
element zeroLength 922 437 438 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 923 439 12 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 80)
node 440 4000 200 14700
rigidLink beam 190 440


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 26), with Mesh Node = 32 (auxiliary for element 80)
node 441 4000 5300 14700
rigidLink beam 161 441

# Extra nodes for zeroLength
# node tag x y z
node 442 4000 200 14700
node 443 4000 5300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 80 0.0 -0.0 1.0
element elasticBeamColumn 80 442 443 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 80

# zero_length_elements zeroLength
element zeroLength 924 440 442 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 925 443 441 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 81)
node 444 4200 0 14700
rigidLink beam 190 444


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 81)
node 445 7800 0 14700
rigidLink beam 191 445

# Extra nodes for zeroLength
# node tag x y z
node 446 4200 0 14700
node 447 7800 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 81 0.0 0.0 1.0
element elasticBeamColumn 81 446 447 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 81

# zero_length_elements zeroLength
element zeroLength 926 444 446 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 927 447 445 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 38), with Mesh Node = 44 (auxiliary for element 82)
node 448 4000 9000 11600
rigidLink beam 44 448


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 82)
node 449 4000 9000 14500
rigidLink beam 65 449
# Geometric transformation command
geomTransf PDelta 82 1.0 0.0 -0.0
element forceBeamColumn 82 448 449 82 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 83)
node 450 4000 14500 8300
rigidLink beam 48 450


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 83)
node 451 4000 14500 11200
rigidLink beam 66 451
# Geometric transformation command
geomTransf PDelta 83 1.0 0.0 -0.0
element forceBeamColumn 83 450 451 83 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 84)
node 452 200 9000 14700
rigidLink beam 194 452


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 84)
node 453 3800 9000 14700
rigidLink beam 192 453

# Extra nodes for zeroLength
# node tag x y z
node 454 200 9000 14700
node 455 3800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 84 0.0 0.0 1.0
element elasticBeamColumn 84 454 455 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 84

# zero_length_elements zeroLength
element zeroLength 928 452 454 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 929 455 453 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 85)
node 456 4000 9200 14700
rigidLink beam 192 456


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 85)
node 457 4000 14300 14700
rigidLink beam 195 457

# Extra nodes for zeroLength
# node tag x y z
node 458 4000 9200 14700
node 459 4000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 85 0.0 -0.0 1.0
element elasticBeamColumn 85 458 459 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 85

# zero_length_elements zeroLength
element zeroLength 930 456 458 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 931 459 457 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 86)
node 460 4000 14500 11600
rigidLink beam 66 460


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 86)
node 461 4000 14500 14500
rigidLink beam 68 461
# Geometric transformation command
geomTransf PDelta 86 1.0 0.0 -0.0
element forceBeamColumn 86 460 461 86 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 87)
node 462 4000 14500 5000
rigidLink beam 69 462


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 87)
node 463 4000 14500 7900
rigidLink beam 48 463
# Geometric transformation command
geomTransf PDelta 87 1.0 0.0 -0.0
element forceBeamColumn 87 462 463 87 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 88)
node 464 4000 14500 14900
rigidLink beam 68 464


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 88)
node 465 4000 14500 17800
rigidLink beam 70 465
# Geometric transformation command
geomTransf PDelta 88 1.0 0.0 -0.0
element forceBeamColumn 88 464 465 88 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 89)
node 466 0 8800 14700
rigidLink beam 194 466

# Extra nodes for zeroLength
# node tag x y z
node 467 0 5500 14700
node 468 0 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 89 0.0 -0.0 1.0
element elasticBeamColumn 89 467 468 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 89

# zero_length_elements zeroLength
element zeroLength 932 14 467 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 933 468 466 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 90)
node 469 0 9200 14700
rigidLink beam 194 469


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 90)
node 470 0 14300 14700
rigidLink beam 198 470

# Extra nodes for zeroLength
# node tag x y z
node 471 0 9200 14700
node 472 0 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 90 0.0 -0.0 1.0
element elasticBeamColumn 90 471 472 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 90

# zero_length_elements zeroLength
element zeroLength 934 469 471 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 935 472 470 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 91)
node 473 4200 9000 14700
rigidLink beam 192 473


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 91)
node 474 7800 9000 14700
rigidLink beam 199 474

# Extra nodes for zeroLength
# node tag x y z
node 475 4200 9000 14700
node 476 7800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 91 0.0 0.0 1.0
element elasticBeamColumn 91 475 476 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 91

# zero_length_elements zeroLength
element zeroLength 936 473 475 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 937 476 474 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 92)
node 477 0 14500 4600
rigidLink beam 53 477
# Geometric transformation command
geomTransf PDelta 92 1.0 0.0 -0.0
element forceBeamColumn 92 73 477 92 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 33), with Mesh Node = 39 (auxiliary for element 93)
node 478 0 5500 4600
rigidLink beam 39 478
# Geometric transformation command
geomTransf PDelta 93 1.0 0.0 -0.0
element forceBeamColumn 93 74 478 93 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 94)
node 479 0 9000 4600
rigidLink beam 52 479
# Geometric transformation command
geomTransf PDelta 94 1.0 0.0 -0.0
element forceBeamColumn 94 75 479 94 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 95)
node 480 4000 9000 4600
rigidLink beam 38 480
# Geometric transformation command
geomTransf PDelta 95 1.0 0.0 -0.0
element forceBeamColumn 95 76 480 95 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 31), with Mesh Node = 37 (auxiliary for element 96)
node 481 0 0 4600
rigidLink beam 37 481
# Geometric transformation command
geomTransf PDelta 96 1.0 0.0 -0.0
element forceBeamColumn 96 77 481 96 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 97)
node 482 4000 14500 4600
rigidLink beam 69 482
# Geometric transformation command
geomTransf PDelta 97 1.0 0.0 -0.0
element forceBeamColumn 97 78 482 97 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 98)
node 483 8000 5500 4600
rigidLink beam 22 483
# Geometric transformation command
geomTransf PDelta 98 1.0 0.0 -0.0
element forceBeamColumn 98 79 483 98 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 99 1.0 0.0 -0.0
element forceBeamColumn 99 80 20 99 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 100 1.0 0.0 -0.0
element forceBeamColumn 100 81 19 100 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 101)
node 484 8000 5500 11200
rigidLink beam 58 484
# Geometric transformation command
geomTransf PDelta 101 1.0 0.0 -0.0
element forceBeamColumn 101 16 484 101 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 102)
node 485 8000 0 8300
rigidLink beam 30 485


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 102)
node 486 8000 0 11200
rigidLink beam 62 486
# Geometric transformation command
geomTransf PDelta 102 1.0 0.0 -0.0
element forceBeamColumn 102 485 486 102 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 103)
node 487 12000 9000 5000
rigidLink beam 82 487


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 103)
node 488 12000 9000 7900
rigidLink beam 28 488
# Geometric transformation command
geomTransf PDelta 103 1.0 0.0 -0.0
element forceBeamColumn 103 487 488 103 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 104)
node 489 12000 5500 8300
rigidLink beam 26 489
# Geometric transformation command
geomTransf PDelta 104 1.0 0.0 -0.0
element forceBeamColumn 104 489 11 104 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 105)
node 490 12000 5500 14500
rigidLink beam 83 490
# Geometric transformation command
geomTransf PDelta 105 1.0 0.0 -0.0
element forceBeamColumn 105 11 490 105 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 106)
node 491 12000 5500 14900
rigidLink beam 83 491
# Geometric transformation command
geomTransf PDelta 106 1.0 0.0 -0.0
element forceBeamColumn 106 491 9 106 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 107)
node 492 8200 5500 11400
rigidLink beam 185 492

# Extra nodes for zeroLength
# node tag x y z
node 493 8200 5500 11400
node 494 12000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 107 0.0 0.0 1.0
element elasticBeamColumn 107 493 494 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 107

# zero_length_elements zeroLength
element zeroLength 938 492 493 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 939 494 11 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 108)
node 495 12000 8800 11400
rigidLink beam 162 495

# Extra nodes for zeroLength
# node tag x y z
node 496 12000 5500 11400
node 497 12000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 108 0.0 -0.0 1.0
element elasticBeamColumn 108 496 497 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 108

# zero_length_elements zeroLength
element zeroLength 940 11 496 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 941 497 495 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 109)
node 498 15800 5500 11400
rigidLink beam 202 498

# Extra nodes for zeroLength
# node tag x y z
node 499 12000 5500 11400
node 500 15800 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 109 0.0 0.0 1.0
element elasticBeamColumn 109 499 500 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 109

# zero_length_elements zeroLength
element zeroLength 942 11 499 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 943 500 498 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 110)
node 501 16000 5700 11400
rigidLink beam 202 501


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 110)
node 502 16000 8800 11400
rigidLink beam 187 502

# Extra nodes for zeroLength
# node tag x y z
node 503 16000 5700 11400
node 504 16000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 110 0.0 -0.0 1.0
element elasticBeamColumn 110 503 504 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 110

# zero_length_elements zeroLength
element zeroLength 944 501 503 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 945 504 502 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 111)
node 505 16200 5500 11400
rigidLink beam 202 505

# Extra nodes for zeroLength
# node tag x y z
node 506 16200 5500 11400
node 507 20000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 111 0.0 0.0 1.0
element elasticBeamColumn 111 506 507 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 111

# zero_length_elements zeroLength
element zeroLength 946 505 506 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 947 507 10 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 112)
node 508 8200 0 11400
rigidLink beam 189 508


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 112)
node 509 11800 0 11400
rigidLink beam 183 509

# Extra nodes for zeroLength
# node tag x y z
node 510 8200 0 11400
node 511 11800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 112 0.0 0.0 1.0
element elasticBeamColumn 112 510 511 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 112

# zero_length_elements zeroLength
element zeroLength 948 508 510 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 949 511 509 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 113)
node 512 12200 0 11400
rigidLink beam 183 512


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 53), with Mesh Node = 59 (auxiliary for element 113)
node 513 15800 0 11400
rigidLink beam 186 513

# Extra nodes for zeroLength
# node tag x y z
node 514 12200 0 11400
node 515 15800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 113 0.0 0.0 1.0
element elasticBeamColumn 113 514 515 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 113

# zero_length_elements zeroLength
element zeroLength 950 512 514 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 951 515 513 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 114)
node 516 4200 14500 14700
rigidLink beam 195 516


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 114)
node 517 7800 14500 14700
rigidLink beam 203 517

# Extra nodes for zeroLength
# node tag x y z
node 518 4200 14500 14700
node 519 7800 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 114 0.0 0.0 1.0
element elasticBeamColumn 114 518 519 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 114

# zero_length_elements zeroLength
element zeroLength 952 516 518 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 953 519 517 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 115)
node 520 3800 14500 18000
rigidLink beam 197 520


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 80), with Mesh Node = 86 (auxiliary for element 115)
node 521 200 14500 18000
rigidLink beam 204 521

# Extra nodes for zeroLength
# node tag x y z
node 522 3800 14500 18000
node 523 200 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 115 0.0 0.0 1.0
element elasticBeamColumn 115 522 523 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 115

# zero_length_elements zeroLength
element zeroLength 954 520 522 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 955 523 521 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 116)
node 524 4000 9200 18000
rigidLink beam 205 524


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 116)
node 525 4000 14300 18000
rigidLink beam 197 525

# Extra nodes for zeroLength
# node tag x y z
node 526 4000 9200 18000
node 527 4000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 116 0.0 -0.0 1.0
element elasticBeamColumn 116 526 527 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 116

# zero_length_elements zeroLength
element zeroLength 956 524 526 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 957 527 525 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 26), with Mesh Node = 32 (auxiliary for element 117)
node 528 4000 5700 14700
rigidLink beam 161 528


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 117)
node 529 4000 8800 14700
rigidLink beam 192 529

# Extra nodes for zeroLength
# node tag x y z
node 530 4000 5700 14700
node 531 4000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 117 0.0 -0.0 1.0
element elasticBeamColumn 117 530 531 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 117

# zero_length_elements zeroLength
element zeroLength 958 528 530 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 959 531 529 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 26), with Mesh Node = 32 (auxiliary for element 118)
node 532 3800 5500 14700
rigidLink beam 161 532

# Extra nodes for zeroLength
# node tag x y z
node 533 0 5500 14700
node 534 3800 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 118 0.0 0.0 1.0
element elasticBeamColumn 118 533 534 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 118

# zero_length_elements zeroLength
element zeroLength 960 14 533 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 961 534 532 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 119)
node 535 0 200 14700
rigidLink beam 206 535

# Extra nodes for zeroLength
# node tag x y z
node 536 0 200 14700
node 537 0 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 119 0.0 -0.0 1.0
element elasticBeamColumn 119 536 537 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 119

# zero_length_elements zeroLength
element zeroLength 962 535 536 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 963 537 14 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 120)
node 538 200 0 14700
rigidLink beam 206 538


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 120)
node 539 3800 0 14700
rigidLink beam 190 539

# Extra nodes for zeroLength
# node tag x y z
node 540 200 0 14700
node 541 3800 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 120 0.0 0.0 1.0
element elasticBeamColumn 120 540 541 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 120

# zero_length_elements zeroLength
element zeroLength 964 538 540 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 965 541 539 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 121)
node 542 200 9000 18000
rigidLink beam 207 542


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 121)
node 543 3800 9000 18000
rigidLink beam 205 543

# Extra nodes for zeroLength
# node tag x y z
node 544 200 9000 18000
node 545 3800 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 121 0.0 0.0 1.0
element elasticBeamColumn 121 544 545 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 121

# zero_length_elements zeroLength
element zeroLength 966 542 544 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 967 545 543 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 122)
node 546 4200 14500 18000
rigidLink beam 197 546


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 84), with Mesh Node = 90 (auxiliary for element 122)
node 547 7800 14500 18000
rigidLink beam 208 547

# Extra nodes for zeroLength
# node tag x y z
node 548 4200 14500 18000
node 549 7800 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 122 0.0 0.0 1.0
element elasticBeamColumn 122 548 549 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 122

# zero_length_elements zeroLength
element zeroLength 968 546 548 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 969 549 547 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 123)
node 550 0 9200 18000
rigidLink beam 207 550


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 80), with Mesh Node = 86 (auxiliary for element 123)
node 551 0 14300 18000
rigidLink beam 204 551

# Extra nodes for zeroLength
# node tag x y z
node 552 0 9200 18000
node 553 0 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 123 0.0 -0.0 1.0
element elasticBeamColumn 123 552 553 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 123

# zero_length_elements zeroLength
element zeroLength 970 550 552 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 971 553 551 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 39), with Mesh Node = 45 (auxiliary for element 124)
node 554 0 5700 11400
rigidLink beam 172 554


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 124)
node 555 0 8800 11400
rigidLink beam 209 555

# Extra nodes for zeroLength
# node tag x y z
node 556 0 5700 11400
node 557 0 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 124 0.0 -0.0 1.0
element elasticBeamColumn 124 556 557 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 124

# zero_length_elements zeroLength
element zeroLength 972 554 556 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 973 557 555 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 125)
node 558 8000 9000 8300
rigidLink beam 25 558


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 40), with Mesh Node = 46 (auxiliary for element 125)
node 559 8000 9000 11200
rigidLink beam 46 559
# Geometric transformation command
geomTransf PDelta 125 1.0 0.0 -0.0
element forceBeamColumn 125 558 559 125 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 126)
node 560 8000 14500 11600
rigidLink beam 61 560


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 126)
node 561 8000 14500 14500
rigidLink beam 85 561
# Geometric transformation command
geomTransf PDelta 126 1.0 0.0 -0.0
element forceBeamColumn 126 560 561 126 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 17), with Mesh Node = 23 (auxiliary for element 127)
node 562 8000 9000 5000
rigidLink beam 23 562


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 127)
node 563 8000 9000 7900
rigidLink beam 25 563
# Geometric transformation command
geomTransf PDelta 127 1.0 0.0 -0.0
element forceBeamColumn 127 562 563 127 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 128)
node 564 8000 14500 8300
rigidLink beam 27 564


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 128)
node 565 8000 14500 11200
rigidLink beam 61 565
# Geometric transformation command
geomTransf PDelta 128 1.0 0.0 -0.0
element forceBeamColumn 128 564 565 128 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 129)
node 566 12000 5500 7900
rigidLink beam 26 566
# Geometric transformation command
geomTransf PDelta 129 1.0 0.0 -0.0
element forceBeamColumn 129 19 566 129 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 35), with Mesh Node = 41 (auxiliary for element 130)
node 567 12000 200 4800
rigidLink beam 168 567

# Extra nodes for zeroLength
# node tag x y z
node 568 12000 200 4800
node 569 12000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 130 0.0 -0.0 1.0
element elasticBeamColumn 130 568 569 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 130

# zero_length_elements zeroLength
element zeroLength 974 567 568 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 975 569 19 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 36), with Mesh Node = 42 (auxiliary for element 131)
node 570 16200 0 4800
rigidLink beam 169 570


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 131)
node 571 19800 0 4800
rigidLink beam 210 571

# Extra nodes for zeroLength
# node tag x y z
node 572 16200 0 4800
node 573 19800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 131 0.0 0.0 1.0
element elasticBeamColumn 131 572 573 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 131

# zero_length_elements zeroLength
element zeroLength 976 570 572 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 977 573 571 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 36), with Mesh Node = 42 (auxiliary for element 132)
node 574 16000 200 4800
rigidLink beam 169 574


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 87), with Mesh Node = 93 (auxiliary for element 132)
node 575 16000 5300 4800
rigidLink beam 211 575

# Extra nodes for zeroLength
# node tag x y z
node 576 16000 200 4800
node 577 16000 5300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 132 0.0 -0.0 1.0
element elasticBeamColumn 132 576 577 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 132

# zero_length_elements zeroLength
element zeroLength 978 574 576 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 979 577 575 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 133)
node 578 8000 14500 5000
rigidLink beam 94 578


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 133)
node 579 8000 14500 7900
rigidLink beam 27 579
# Geometric transformation command
geomTransf PDelta 133 1.0 0.0 -0.0
element forceBeamColumn 133 578 579 133 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 34), with Mesh Node = 40 (auxiliary for element 134)
node 580 8000 200 4800
rigidLink beam 167 580


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 134)
node 581 8000 5300 4800
rigidLink beam 151 581

# Extra nodes for zeroLength
# node tag x y z
node 582 8000 200 4800
node 583 8000 5300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 134 0.0 -0.0 1.0
element elasticBeamColumn 134 582 583 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 134

# zero_length_elements zeroLength
element zeroLength 980 580 582 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 981 583 581 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 17), with Mesh Node = 23 (auxiliary for element 135)
node 584 8200 9000 4800
rigidLink beam 152 584


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 135)
node 585 11800 9000 4800
rigidLink beam 200 585

# Extra nodes for zeroLength
# node tag x y z
node 586 8200 9000 4800
node 587 11800 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 135 0.0 0.0 1.0
element elasticBeamColumn 135 586 587 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 135

# zero_length_elements zeroLength
element zeroLength 982 584 586 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 983 587 585 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 87), with Mesh Node = 93 (auxiliary for element 136)
node 588 15800 5500 4800
rigidLink beam 211 588

# Extra nodes for zeroLength
# node tag x y z
node 589 12000 5500 4800
node 590 15800 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 136 0.0 0.0 1.0
element elasticBeamColumn 136 589 590 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 136

# zero_length_elements zeroLength
element zeroLength 984 19 589 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 985 590 588 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 87), with Mesh Node = 93 (auxiliary for element 137)
node 591 16200 5500 4800
rigidLink beam 211 591

# Extra nodes for zeroLength
# node tag x y z
node 592 16200 5500 4800
node 593 20000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 137 0.0 0.0 1.0
element elasticBeamColumn 137 592 593 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 137

# zero_length_elements zeroLength
element zeroLength 986 591 592 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 987 593 18 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 138)
node 594 12000 8800 4800
rigidLink beam 200 594

# Extra nodes for zeroLength
# node tag x y z
node 595 12000 5500 4800
node 596 12000 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 138 0.0 -0.0 1.0
element elasticBeamColumn 138 595 596 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 138

# zero_length_elements zeroLength
element zeroLength 988 19 595 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 989 596 594 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 17), with Mesh Node = 23 (auxiliary for element 139)
node 597 8000 9200 4800
rigidLink beam 152 597


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 139)
node 598 8000 14300 4800
rigidLink beam 212 598

# Extra nodes for zeroLength
# node tag x y z
node 599 8000 9200 4800
node 600 8000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 139 0.0 -0.0 1.0
element elasticBeamColumn 139 599 600 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 139

# zero_length_elements zeroLength
element zeroLength 990 597 599 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 991 600 598 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 140)
node 601 20000 200 4800
rigidLink beam 210 601

# Extra nodes for zeroLength
# node tag x y z
node 602 20000 200 4800
node 603 20000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 140 0.0 -0.0 1.0
element elasticBeamColumn 140 602 603 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 140

# zero_length_elements zeroLength
element zeroLength 992 601 602 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 993 603 18 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 141)
node 604 12000 9200 4800
rigidLink beam 200 604


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 141)
node 605 12000 14300 4800
rigidLink beam 213 605

# Extra nodes for zeroLength
# node tag x y z
node 606 12000 9200 4800
node 607 12000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 141 0.0 -0.0 1.0
element elasticBeamColumn 141 606 607 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 141

# zero_length_elements zeroLength
element zeroLength 994 604 606 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 995 607 605 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 142)
node 608 8000 200 11400
rigidLink beam 189 608


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 142)
node 609 8000 5300 11400
rigidLink beam 185 609

# Extra nodes for zeroLength
# node tag x y z
node 610 8000 200 11400
node 611 8000 5300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 142 0.0 -0.0 1.0
element elasticBeamColumn 142 610 611 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 142

# zero_length_elements zeroLength
element zeroLength 996 608 610 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 997 611 609 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 53), with Mesh Node = 59 (auxiliary for element 143)
node 612 16000 200 11400
rigidLink beam 186 612


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 143)
node 613 16000 5300 11400
rigidLink beam 202 613

# Extra nodes for zeroLength
# node tag x y z
node 614 16000 200 11400
node 615 16000 5300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 143 0.0 -0.0 1.0
element elasticBeamColumn 143 614 615 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 143

# zero_length_elements zeroLength
element zeroLength 998 612 614 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 999 615 613 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 144)
node 616 12000 5700 14700
rigidLink beam 201 616


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 144)
node 617 12000 8800 14700
rigidLink beam 214 617

# Extra nodes for zeroLength
# node tag x y z
node 618 12000 5700 14700
node 619 12000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 144 0.0 -0.0 1.0
element elasticBeamColumn 144 618 619 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 144

# zero_length_elements zeroLength
element zeroLength 1000 616 618 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1001 619 617 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 145)
node 620 12000 200 11400
rigidLink beam 183 620

# Extra nodes for zeroLength
# node tag x y z
node 621 12000 200 11400
node 622 12000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 145 0.0 -0.0 1.0
element elasticBeamColumn 145 621 622 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 145

# zero_length_elements zeroLength
element zeroLength 1002 620 621 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1003 622 11 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 53), with Mesh Node = 59 (auxiliary for element 146)
node 623 16200 0 11400
rigidLink beam 186 623


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 146)
node 624 19800 0 11400
rigidLink beam 215 624

# Extra nodes for zeroLength
# node tag x y z
node 625 16200 0 11400
node 626 19800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 146 0.0 0.0 1.0
element elasticBeamColumn 146 625 626 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 146

# zero_length_elements zeroLength
element zeroLength 1004 623 625 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1005 626 624 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 147)
node 627 12000 9200 14700
rigidLink beam 214 627


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 147)
node 628 12000 14300 14700
rigidLink beam 216 628

# Extra nodes for zeroLength
# node tag x y z
node 629 12000 9200 14700
node 630 12000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 147 0.0 -0.0 1.0
element elasticBeamColumn 147 629 630 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 147

# zero_length_elements zeroLength
element zeroLength 1006 627 629 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1007 630 628 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 148)
node 631 12200 5500 14700
rigidLink beam 201 631

# Extra nodes for zeroLength
# node tag x y z
node 632 12200 5500 14700
node 633 16000 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 148 0.0 0.0 1.0
element elasticBeamColumn 148 632 633 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 148

# zero_length_elements zeroLength
element zeroLength 1008 631 632 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1009 633 7 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 93), with Mesh Node = 99 (auxiliary for element 149)
node 634 19800 5500 14700
rigidLink beam 217 634

# Extra nodes for zeroLength
# node tag x y z
node 635 16000 5500 14700
node 636 19800 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 149 0.0 0.0 1.0
element elasticBeamColumn 149 635 636 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 149

# zero_length_elements zeroLength
element zeroLength 1010 7 635 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1011 636 634 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 150)
node 637 11800 5500 14700
rigidLink beam 201 637

# Extra nodes for zeroLength
# node tag x y z
node 638 8000 5500 14700
node 639 11800 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 150 0.0 0.0 1.0
element elasticBeamColumn 150 638 639 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 150

# zero_length_elements zeroLength
element zeroLength 1012 12 638 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1013 639 637 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 151)
node 640 20000 200 14700
rigidLink beam 218 640


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 93), with Mesh Node = 99 (auxiliary for element 151)
node 641 20000 5300 14700
rigidLink beam 217 641

# Extra nodes for zeroLength
# node tag x y z
node 642 20000 200 14700
node 643 20000 5300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 151 0.0 -0.0 1.0
element elasticBeamColumn 151 642 643 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 151

# zero_length_elements zeroLength
element zeroLength 1014 640 642 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1015 643 641 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 152)
node 644 16000 14500 8300
rigidLink beam 101 644


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 51), with Mesh Node = 57 (auxiliary for element 152)
node 645 16000 14500 11200
rigidLink beam 57 645
# Geometric transformation command
geomTransf PDelta 152 1.0 0.0 -0.0
element forceBeamColumn 152 644 645 152 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 51), with Mesh Node = 57 (auxiliary for element 153)
node 646 16000 14500 11600
rigidLink beam 57 646


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 153)
node 647 16000 14500 14500
rigidLink beam 102 647
# Geometric transformation command
geomTransf PDelta 153 1.0 0.0 -0.0
element forceBeamColumn 153 646 647 153 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 154)
node 648 16000 14500 14900
rigidLink beam 102 648


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 154)
node 649 16000 14500 17800
rigidLink beam 103 649
# Geometric transformation command
geomTransf PDelta 154 1.0 0.0 -0.0
element forceBeamColumn 154 648 649 154 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 155)
node 650 8000 200 14700
rigidLink beam 191 650

# Extra nodes for zeroLength
# node tag x y z
node 651 8000 200 14700
node 652 8000 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 155 0.0 -0.0 1.0
element elasticBeamColumn 155 651 652 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 155

# zero_length_elements zeroLength
element zeroLength 1016 650 651 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1017 652 12 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 156)
node 653 16200 14500 18000
rigidLink beam 221 653


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 98), with Mesh Node = 104 (auxiliary for element 156)
node 654 19800 14500 18000
rigidLink beam 222 654

# Extra nodes for zeroLength
# node tag x y z
node 655 16200 14500 18000
node 656 19800 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 156 0.0 0.0 1.0
element elasticBeamColumn 156 655 656 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 156

# zero_length_elements zeroLength
element zeroLength 1018 653 655 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1019 656 654 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 157)
node 657 8200 5500 18000
rigidLink beam 223 657

# Extra nodes for zeroLength
# node tag x y z
node 658 8200 5500 18000
node 659 12000 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 157 0.0 0.0 1.0
element elasticBeamColumn 157 658 659 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 157

# zero_length_elements zeroLength
element zeroLength 1020 657 658 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1021 659 9 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 158)
node 660 16000 14300 18000
rigidLink beam 221 660

# Extra nodes for zeroLength
# node tag x y z
node 661 16000 9000 18000
node 662 16000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 158 0.0 -0.0 1.0
element elasticBeamColumn 158 661 662 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 158

# zero_length_elements zeroLength
element zeroLength 1022 8 661 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1023 662 660 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 159)
node 663 16000 5700 18000
rigidLink beam 224 663

# Extra nodes for zeroLength
# node tag x y z
node 664 16000 5700 18000
node 665 16000 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 159 0.0 -0.0 1.0
element elasticBeamColumn 159 664 665 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 159

# zero_length_elements zeroLength
element zeroLength 1024 663 664 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1025 665 8 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 160)
node 666 12000 8800 18000
rigidLink beam 225 666

# Extra nodes for zeroLength
# node tag x y z
node 667 12000 5500 18000
node 668 12000 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 160 0.0 -0.0 1.0
element elasticBeamColumn 160 667 668 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 160

# zero_length_elements zeroLength
element zeroLength 1026 9 667 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1027 668 666 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 161)
node 669 15800 5500 18000
rigidLink beam 224 669

# Extra nodes for zeroLength
# node tag x y z
node 670 12000 5500 18000
node 671 15800 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 161 0.0 0.0 1.0
element elasticBeamColumn 161 670 671 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 161

# zero_length_elements zeroLength
element zeroLength 1028 9 670 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1029 671 669 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 102), with Mesh Node = 108 (auxiliary for element 162)
node 672 20000 9200 18000
rigidLink beam 226 672


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 98), with Mesh Node = 104 (auxiliary for element 162)
node 673 20000 14300 18000
rigidLink beam 222 673

# Extra nodes for zeroLength
# node tag x y z
node 674 20000 9200 18000
node 675 20000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 162 0.0 -0.0 1.0
element elasticBeamColumn 162 674 675 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 162

# zero_length_elements zeroLength
element zeroLength 1030 672 674 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1031 675 673 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 163)
node 676 12000 9200 8100
rigidLink beam 157 676


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 163)
node 677 12000 14300 8100
rigidLink beam 227 677

# Extra nodes for zeroLength
# node tag x y z
node 678 12000 9200 8100
node 679 12000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 163 0.0 -0.0 1.0
element elasticBeamColumn 163 678 679 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 163

# zero_length_elements zeroLength
element zeroLength 1032 676 678 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1033 679 677 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 164)
node 680 12000 14500 5000
rigidLink beam 95 680


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 164)
node 681 12000 14500 7900
rigidLink beam 109 681
# Geometric transformation command
geomTransf PDelta 164 1.0 0.0 -0.0
element forceBeamColumn 164 680 681 164 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 104), with Mesh Node = 110 (auxiliary for element 165)
node 682 20000 5700 18000
rigidLink beam 228 682


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 102), with Mesh Node = 108 (auxiliary for element 165)
node 683 20000 8800 18000
rigidLink beam 226 683

# Extra nodes for zeroLength
# node tag x y z
node 684 20000 5700 18000
node 685 20000 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 165 0.0 -0.0 1.0
element elasticBeamColumn 165 684 685 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 165

# zero_length_elements zeroLength
element zeroLength 1034 682 684 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1035 685 683 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 166)
node 686 16200 5500 18000
rigidLink beam 224 686


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 104), with Mesh Node = 110 (auxiliary for element 166)
node 687 19800 5500 18000
rigidLink beam 228 687

# Extra nodes for zeroLength
# node tag x y z
node 688 16200 5500 18000
node 689 19800 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 166 0.0 0.0 1.0
element elasticBeamColumn 166 688 689 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 166

# zero_length_elements zeroLength
element zeroLength 1036 686 688 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1037 689 687 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 167)
node 690 16200 14500 8100
rigidLink beam 219 690


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 105), with Mesh Node = 111 (auxiliary for element 167)
node 691 19800 14500 8100
rigidLink beam 229 691

# Extra nodes for zeroLength
# node tag x y z
node 692 16200 14500 8100
node 693 19800 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 167 0.0 0.0 1.0
element elasticBeamColumn 167 692 693 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 167

# zero_length_elements zeroLength
element zeroLength 1038 690 692 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1039 693 691 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 168)
node 694 12000 14500 11600
rigidLink beam 34 694


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 168)
node 695 12000 14500 14500
rigidLink beam 98 695
# Geometric transformation command
geomTransf PDelta 168 1.0 0.0 -0.0
element forceBeamColumn 168 694 695 168 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 169)
node 696 12200 14500 8100
rigidLink beam 227 696


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 169)
node 697 15800 14500 8100
rigidLink beam 219 697

# Extra nodes for zeroLength
# node tag x y z
node 698 12200 14500 8100
node 699 15800 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 169 0.0 0.0 1.0
element elasticBeamColumn 169 698 699 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 169

# zero_length_elements zeroLength
element zeroLength 1040 696 698 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1041 699 697 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 170)
node 700 16000 9200 8100
rigidLink beam 230 700


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 170)
node 701 16000 14300 8100
rigidLink beam 219 701

# Extra nodes for zeroLength
# node tag x y z
node 702 16000 9200 8100
node 703 16000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 170 0.0 -0.0 1.0
element elasticBeamColumn 170 702 703 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 170

# zero_length_elements zeroLength
element zeroLength 1042 700 702 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1043 703 701 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 107), with Mesh Node = 113 (auxiliary for element 171)
node 704 8000 200 18000
rigidLink beam 231 704


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 171)
node 705 8000 5300 18000
rigidLink beam 223 705

# Extra nodes for zeroLength
# node tag x y z
node 706 8000 200 18000
node 707 8000 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 171 0.0 -0.0 1.0
element elasticBeamColumn 171 706 707 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 171

# zero_length_elements zeroLength
element zeroLength 1044 704 706 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1045 707 705 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 172)
node 708 20000 9200 8100
rigidLink beam 232 708


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 105), with Mesh Node = 111 (auxiliary for element 172)
node 709 20000 14300 8100
rigidLink beam 229 709

# Extra nodes for zeroLength
# node tag x y z
node 710 20000 9200 8100
node 711 20000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 172 0.0 -0.0 1.0
element elasticBeamColumn 172 710 711 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 172

# zero_length_elements zeroLength
element zeroLength 1046 708 710 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1047 711 709 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 173)
node 712 8200 14500 11400
rigidLink beam 188 712


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 173)
node 713 11800 14500 11400
rigidLink beam 163 713

# Extra nodes for zeroLength
# node tag x y z
node 714 8200 14500 11400
node 715 11800 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 173 0.0 0.0 1.0
element elasticBeamColumn 173 714 715 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 173

# zero_length_elements zeroLength
element zeroLength 1048 712 714 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1049 715 713 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 174)
node 716 12000 14500 8300
rigidLink beam 109 716


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 174)
node 717 12000 14500 11200
rigidLink beam 34 717
# Geometric transformation command
geomTransf PDelta 174 1.0 0.0 -0.0
element forceBeamColumn 174 716 717 174 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 175)
node 718 8000 0 14900
rigidLink beam 64 718


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 107), with Mesh Node = 113 (auxiliary for element 175)
node 719 8000 0 17800
rigidLink beam 113 719
# Geometric transformation command
geomTransf PDelta 175 1.0 0.0 -0.0
element forceBeamColumn 175 718 719 175 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 176)
node 720 20000 5500 7900
rigidLink beam 115 720
# Geometric transformation command
geomTransf PDelta 176 1.0 0.0 -0.0
element forceBeamColumn 176 18 720 176 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 87), with Mesh Node = 93 (auxiliary for element 177)
node 721 16000 5500 5000
rigidLink beam 93 721
# Geometric transformation command
geomTransf PDelta 177 1.0 0.0 -0.0
element forceBeamColumn 177 721 15 177 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 178)
node 722 8000 0 11600
rigidLink beam 62 722


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 178)
node 723 8000 0 14500
rigidLink beam 64 723
# Geometric transformation command
geomTransf PDelta 178 1.0 0.0 -0.0
element forceBeamColumn 178 722 723 178 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 179)
node 724 16000 9000 5000
rigidLink beam 116 724


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 179)
node 725 16000 9000 7900
rigidLink beam 112 725
# Geometric transformation command
geomTransf PDelta 179 1.0 0.0 -0.0
element forceBeamColumn 179 724 725 179 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 180)
node 726 16000 9000 8300
rigidLink beam 112 726


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 180)
node 727 16000 9000 11200
rigidLink beam 60 727
# Geometric transformation command
geomTransf PDelta 180 1.0 0.0 -0.0
element forceBeamColumn 180 726 727 180 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 181)
node 728 16000 9000 11600
rigidLink beam 60 728


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 181)
node 729 16000 9000 14500
rigidLink beam 117 729
# Geometric transformation command
geomTransf PDelta 181 1.0 0.0 -0.0
element forceBeamColumn 181 728 729 181 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 93), with Mesh Node = 99 (auxiliary for element 182)
node 730 20000 5500 14900
rigidLink beam 99 730


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 104), with Mesh Node = 110 (auxiliary for element 182)
node 731 20000 5500 17800
rigidLink beam 110 731
# Geometric transformation command
geomTransf PDelta 182 1.0 0.0 -0.0
element forceBeamColumn 182 730 731 182 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 93), with Mesh Node = 99 (auxiliary for element 183)
node 732 20000 5500 14500
rigidLink beam 99 732
# Geometric transformation command
geomTransf PDelta 183 1.0 0.0 -0.0
element forceBeamColumn 183 10 732 183 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 184)
node 733 8200 14500 8100
rigidLink beam 156 733


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 184)
node 734 11800 14500 8100
rigidLink beam 227 734

# Extra nodes for zeroLength
# node tag x y z
node 735 8200 14500 8100
node 736 11800 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 184 0.0 0.0 1.0
element elasticBeamColumn 184 735 736 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 184

# zero_length_elements zeroLength
element zeroLength 1050 733 735 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1051 736 734 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 185)
node 737 12200 5500 8100
rigidLink beam 155 737

# Extra nodes for zeroLength
# node tag x y z
node 738 12200 5500 8100
node 739 16000 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 185 0.0 0.0 1.0
element elasticBeamColumn 185 738 739 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 185

# zero_length_elements zeroLength
element zeroLength 1052 737 738 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1053 739 15 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 186)
node 740 16200 9000 8100
rigidLink beam 230 740


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 186)
node 741 19800 9000 8100
rigidLink beam 232 741

# Extra nodes for zeroLength
# node tag x y z
node 742 16200 9000 8100
node 743 19800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 186 0.0 0.0 1.0
element elasticBeamColumn 186 742 743 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 186

# zero_length_elements zeroLength
element zeroLength 1054 740 742 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1055 743 741 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 187)
node 744 8200 9000 8100
rigidLink beam 154 744


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 187)
node 745 11800 9000 8100
rigidLink beam 157 745

# Extra nodes for zeroLength
# node tag x y z
node 746 8200 9000 8100
node 747 11800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 187 0.0 0.0 1.0
element elasticBeamColumn 187 746 747 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 187

# zero_length_elements zeroLength
element zeroLength 1056 744 746 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1057 747 745 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 188)
node 748 12200 9000 8100
rigidLink beam 157 748


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 188)
node 749 15800 9000 8100
rigidLink beam 230 749

# Extra nodes for zeroLength
# node tag x y z
node 750 12200 9000 8100
node 751 15800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 188 0.0 0.0 1.0
element elasticBeamColumn 188 750 751 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 188

# zero_length_elements zeroLength
element zeroLength 1058 748 750 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1059 751 749 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 189)
node 752 19800 5500 8100
rigidLink beam 233 752

# Extra nodes for zeroLength
# node tag x y z
node 753 16000 5500 8100
node 754 19800 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 189 0.0 0.0 1.0
element elasticBeamColumn 189 753 754 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 189

# zero_length_elements zeroLength
element zeroLength 1060 15 753 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1061 754 752 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 190)
node 755 16000 8800 8100
rigidLink beam 230 755

# Extra nodes for zeroLength
# node tag x y z
node 756 16000 5500 8100
node 757 16000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 190 0.0 -0.0 1.0
element elasticBeamColumn 190 756 757 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 190

# zero_length_elements zeroLength
element zeroLength 1062 15 756 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1063 757 755 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 191)
node 758 16200 0 8100
rigidLink beam 174 758


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 112), with Mesh Node = 118 (auxiliary for element 191)
node 759 19800 0 8100
rigidLink beam 236 759

# Extra nodes for zeroLength
# node tag x y z
node 760 16200 0 8100
node 761 19800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 191 0.0 0.0 1.0
element elasticBeamColumn 191 760 761 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 191

# zero_length_elements zeroLength
element zeroLength 1064 758 760 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1065 761 759 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 192)
node 762 20000 5700 8100
rigidLink beam 233 762


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 192)
node 763 20000 8800 8100
rigidLink beam 232 763

# Extra nodes for zeroLength
# node tag x y z
node 764 20000 5700 8100
node 765 20000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 192 0.0 -0.0 1.0
element elasticBeamColumn 192 764 765 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 192

# zero_length_elements zeroLength
element zeroLength 1066 762 764 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1067 765 763 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 193)
node 766 4200 0 8100
rigidLink beam 158 766


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 193)
node 767 7800 0 8100
rigidLink beam 159 767

# Extra nodes for zeroLength
# node tag x y z
node 768 4200 0 8100
node 769 7800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 193 0.0 0.0 1.0
element elasticBeamColumn 193 768 769 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 193

# zero_length_elements zeroLength
element zeroLength 1068 766 768 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1069 769 767 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 194)
node 770 12200 0 8100
rigidLink beam 160 770


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 194)
node 771 15800 0 8100
rigidLink beam 174 771

# Extra nodes for zeroLength
# node tag x y z
node 772 12200 0 8100
node 773 15800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 194 0.0 0.0 1.0
element elasticBeamColumn 194 772 773 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 194

# zero_length_elements zeroLength
element zeroLength 1070 770 772 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1071 773 771 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 112), with Mesh Node = 118 (auxiliary for element 195)
node 774 20000 200 8100
rigidLink beam 236 774


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 195)
node 775 20000 5300 8100
rigidLink beam 233 775

# Extra nodes for zeroLength
# node tag x y z
node 776 20000 200 8100
node 777 20000 5300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 195 0.0 -0.0 1.0
element elasticBeamColumn 195 776 777 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 195

# zero_length_elements zeroLength
element zeroLength 1072 774 776 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1073 777 775 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 196)
node 778 8200 0 8100
rigidLink beam 159 778


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 196)
node 779 11800 0 8100
rigidLink beam 160 779

# Extra nodes for zeroLength
# node tag x y z
node 780 8200 0 8100
node 781 11800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 196 0.0 0.0 1.0
element elasticBeamColumn 196 780 781 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 196

# zero_length_elements zeroLength
element zeroLength 1074 778 780 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1075 781 779 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 197)
node 782 8000 14500 14900
rigidLink beam 85 782


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 84), with Mesh Node = 90 (auxiliary for element 197)
node 783 8000 14500 17800
rigidLink beam 90 783
# Geometric transformation command
geomTransf PDelta 197 1.0 0.0 -0.0
element forceBeamColumn 197 782 783 197 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 198)
node 784 16000 200 8100
rigidLink beam 174 784

# Extra nodes for zeroLength
# node tag x y z
node 785 16000 200 8100
node 786 16000 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 198 0.0 -0.0 1.0
element elasticBeamColumn 198 785 786 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 198

# zero_length_elements zeroLength
element zeroLength 1076 784 785 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1077 786 15 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 199)
node 787 8000 9000 14900
rigidLink beam 72 787


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 199)
node 788 8000 9000 17800
rigidLink beam 119 788
# Geometric transformation command
geomTransf PDelta 199 1.0 0.0 -0.0
element forceBeamColumn 199 787 788 199 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 40), with Mesh Node = 46 (auxiliary for element 200)
node 789 8000 9000 11600
rigidLink beam 46 789


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 200)
node 790 8000 9000 14500
rigidLink beam 72 790
# Geometric transformation command
geomTransf PDelta 200 1.0 0.0 -0.0
element forceBeamColumn 200 789 790 200 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 201)
node 791 3800 14500 14700
rigidLink beam 195 791


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 201)
node 792 200 14500 14700
rigidLink beam 198 792

# Extra nodes for zeroLength
# node tag x y z
node 793 3800 14500 14700
node 794 200 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 201 0.0 0.0 1.0
element elasticBeamColumn 201 793 794 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 201

# zero_length_elements zeroLength
element zeroLength 1078 791 793 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1079 794 792 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 26), with Mesh Node = 32 (auxiliary for element 202)
node 795 4000 5500 14900
rigidLink beam 32 795


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 202)
node 796 4000 5500 17800
rigidLink beam 120 796
# Geometric transformation command
geomTransf PDelta 202 1.0 0.0 -0.0
element forceBeamColumn 202 795 796 202 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 203)
node 797 4000 9000 14900
rigidLink beam 65 797


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 203)
node 798 4000 9000 17800
rigidLink beam 87 798
# Geometric transformation command
geomTransf PDelta 203 1.0 0.0 -0.0
element forceBeamColumn 203 797 798 203 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 204)
node 799 4200 9000 18000
rigidLink beam 205 799


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 204)
node 800 7800 9000 18000
rigidLink beam 237 800

# Extra nodes for zeroLength
# node tag x y z
node 801 4200 9000 18000
node 802 7800 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 204 0.0 0.0 1.0
element elasticBeamColumn 204 801 802 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 204

# zero_length_elements zeroLength
element zeroLength 1080 799 801 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1081 802 800 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 205)
node 803 4000 9200 4800
rigidLink beam 165 803


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 205)
node 804 4000 14300 4800
rigidLink beam 196 804

# Extra nodes for zeroLength
# node tag x y z
node 805 4000 9200 4800
node 806 4000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 205 0.0 -0.0 1.0
element elasticBeamColumn 205 805 806 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 205

# zero_length_elements zeroLength
element zeroLength 1082 803 805 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1083 806 804 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 33), with Mesh Node = 39 (auxiliary for element 206)
node 807 0 5700 4800
rigidLink beam 166 807


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 206)
node 808 0 8800 4800
rigidLink beam 179 808

# Extra nodes for zeroLength
# node tag x y z
node 809 0 5700 4800
node 810 0 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 206 0.0 -0.0 1.0
element elasticBeamColumn 206 809 810 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 206

# zero_length_elements zeroLength
element zeroLength 1084 807 809 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1085 810 808 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 207)
node 811 0 9200 11400
rigidLink beam 209 811


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 48), with Mesh Node = 54 (auxiliary for element 207)
node 812 0 14300 11400
rigidLink beam 181 812

# Extra nodes for zeroLength
# node tag x y z
node 813 0 9200 11400
node 814 0 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 207 0.0 -0.0 1.0
element elasticBeamColumn 207 813 814 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 207

# zero_length_elements zeroLength
element zeroLength 1086 811 813 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1087 814 812 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 208)
node 815 200 9000 4800
rigidLink beam 179 815


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 208)
node 816 3800 9000 4800
rigidLink beam 165 816

# Extra nodes for zeroLength
# node tag x y z
node 817 200 9000 4800
node 818 3800 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 208 0.0 0.0 1.0
element elasticBeamColumn 208 817 818 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 208

# zero_length_elements zeroLength
element zeroLength 1088 815 817 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1089 818 816 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 209)
node 819 0 9200 4800
rigidLink beam 179 819


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 209)
node 820 0 14300 4800
rigidLink beam 180 820

# Extra nodes for zeroLength
# node tag x y z
node 821 0 9200 4800
node 822 0 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 209 0.0 -0.0 1.0
element elasticBeamColumn 209 821 822 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 209

# zero_length_elements zeroLength
element zeroLength 1090 819 821 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1091 822 820 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 210)
node 823 3800 14500 4800
rigidLink beam 196 823


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 210)
node 824 200 14500 4800
rigidLink beam 180 824

# Extra nodes for zeroLength
# node tag x y z
node 825 3800 14500 4800
node 826 200 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 210 0.0 0.0 1.0
element elasticBeamColumn 210 825 826 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 210

# zero_length_elements zeroLength
element zeroLength 1092 823 825 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1093 826 824 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 39), with Mesh Node = 45 (auxiliary for element 211)
node 827 0 5500 11600
rigidLink beam 45 827
# Geometric transformation command
geomTransf PDelta 211 1.0 0.0 -0.0
element forceBeamColumn 211 827 14 211 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 212)
node 828 0 14500 14900
rigidLink beam 71 828


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 80), with Mesh Node = 86 (auxiliary for element 212)
node 829 0 14500 17800
rigidLink beam 86 829
# Geometric transformation command
geomTransf PDelta 212 1.0 0.0 -0.0
element forceBeamColumn 212 828 829 212 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 43), with Mesh Node = 49 (auxiliary for element 213)
node 830 0 9000 8300
rigidLink beam 49 830


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 213)
node 831 0 9000 11200
rigidLink beam 91 831
# Geometric transformation command
geomTransf PDelta 213 1.0 0.0 -0.0
element forceBeamColumn 213 830 831 213 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 33), with Mesh Node = 39 (auxiliary for element 214)
node 832 0 5500 5000
rigidLink beam 39 832
# Geometric transformation command
geomTransf PDelta 214 1.0 0.0 -0.0
element forceBeamColumn 214 832 17 214 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 215)
node 833 0 9000 14900
rigidLink beam 67 833


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 215)
node 834 0 9000 17800
rigidLink beam 89 834
# Geometric transformation command
geomTransf PDelta 215 1.0 0.0 -0.0
element forceBeamColumn 215 833 834 215 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 39), with Mesh Node = 45 (auxiliary for element 216)
node 835 0 5500 11200
rigidLink beam 45 835
# Geometric transformation command
geomTransf PDelta 216 1.0 0.0 -0.0
element forceBeamColumn 216 17 835 216 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 45), with Mesh Node = 51 (auxiliary for element 217)
node 836 0 0 8300
rigidLink beam 51 836


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 115), with Mesh Node = 121 (auxiliary for element 217)
node 837 0 0 11200
rigidLink beam 121 837
# Geometric transformation command
geomTransf PDelta 217 1.0 0.0 -0.0
element forceBeamColumn 217 836 837 217 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 218)
node 838 0 0 14900
rigidLink beam 88 838


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 116), with Mesh Node = 122 (auxiliary for element 218)
node 839 0 0 17800
rigidLink beam 122 839
# Geometric transformation command
geomTransf PDelta 218 1.0 0.0 -0.0
element forceBeamColumn 218 838 839 218 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 219)
node 840 0 5500 17800
rigidLink beam 123 840
# Geometric transformation command
geomTransf PDelta 219 1.0 0.0 -0.0
element forceBeamColumn 219 14 840 219 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 31), with Mesh Node = 37 (auxiliary for element 220)
node 841 0 0 5000
rigidLink beam 37 841


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 45), with Mesh Node = 51 (auxiliary for element 220)
node 842 0 0 7900
rigidLink beam 51 842
# Geometric transformation command
geomTransf PDelta 220 1.0 0.0 -0.0
element forceBeamColumn 220 841 842 220 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 221)
node 843 3800 14500 11400
rigidLink beam 193 843


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 48), with Mesh Node = 54 (auxiliary for element 221)
node 844 200 14500 11400
rigidLink beam 181 844

# Extra nodes for zeroLength
# node tag x y z
node 845 3800 14500 11400
node 846 200 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 221 0.0 0.0 1.0
element elasticBeamColumn 221 845 846 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 221

# zero_length_elements zeroLength
element zeroLength 1094 843 845 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1095 846 844 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 115), with Mesh Node = 121 (auxiliary for element 222)
node 847 0 0 11600
rigidLink beam 121 847


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 222)
node 848 0 0 14500
rigidLink beam 88 848
# Geometric transformation command
geomTransf PDelta 222 1.0 0.0 -0.0
element forceBeamColumn 222 847 848 222 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 38), with Mesh Node = 44 (auxiliary for element 223)
node 849 4000 9200 11400
rigidLink beam 171 849


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 223)
node 850 4000 14300 11400
rigidLink beam 193 850

# Extra nodes for zeroLength
# node tag x y z
node 851 4000 9200 11400
node 852 4000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 223 0.0 -0.0 1.0
element elasticBeamColumn 223 851 852 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 223

# zero_length_elements zeroLength
element zeroLength 1096 849 851 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1097 852 850 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 224)
node 853 200 9000 11400
rigidLink beam 209 853


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 38), with Mesh Node = 44 (auxiliary for element 224)
node 854 3800 9000 11400
rigidLink beam 171 854

# Extra nodes for zeroLength
# node tag x y z
node 855 200 9000 11400
node 856 3800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 224 0.0 0.0 1.0
element elasticBeamColumn 224 855 856 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 224

# zero_length_elements zeroLength
element zeroLength 1098 853 855 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1099 856 854 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 225)
node 857 12000 9000 11600
rigidLink beam 33 857


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 225)
node 858 12000 9000 14500
rigidLink beam 96 858
# Geometric transformation command
geomTransf PDelta 225 1.0 0.0 -0.0
element forceBeamColumn 225 857 858 225 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 226)
node 859 20000 9000 14900
rigidLink beam 124 859


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 102), with Mesh Node = 108 (auxiliary for element 226)
node 860 20000 9000 17800
rigidLink beam 108 860
# Geometric transformation command
geomTransf PDelta 226 1.0 0.0 -0.0
element forceBeamColumn 226 859 860 226 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 227)
node 861 12000 9000 14900
rigidLink beam 96 861


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 227)
node 862 12000 9000 17800
rigidLink beam 107 862
# Geometric transformation command
geomTransf PDelta 227 1.0 0.0 -0.0
element forceBeamColumn 227 861 862 227 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 228)
node 863 16000 9000 14900
rigidLink beam 117 863
# Geometric transformation command
geomTransf PDelta 228 1.0 0.0 -0.0
element forceBeamColumn 228 863 8 228 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 229)
node 864 8000 5500 11600
rigidLink beam 58 864
# Geometric transformation command
geomTransf PDelta 229 1.0 0.0 -0.0
element forceBeamColumn 229 864 12 229 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 230)
node 865 8000 5500 17800
rigidLink beam 105 865
# Geometric transformation command
geomTransf PDelta 230 1.0 0.0 -0.0
element forceBeamColumn 230 12 865 230 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 231)
node 866 20000 9000 8300
rigidLink beam 114 866


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 231)
node 867 20000 9000 11200
rigidLink beam 125 867
# Geometric transformation command
geomTransf PDelta 231 1.0 0.0 -0.0
element forceBeamColumn 231 866 867 231 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 105), with Mesh Node = 111 (auxiliary for element 232)
node 868 20000 14500 8300
rigidLink beam 111 868


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 120), with Mesh Node = 126 (auxiliary for element 232)
node 869 20000 14500 11200
rigidLink beam 126 869
# Geometric transformation command
geomTransf PDelta 232 1.0 0.0 -0.0
element forceBeamColumn 232 868 869 232 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 121), with Mesh Node = 127 (auxiliary for element 233)
node 870 20000 9000 5000
rigidLink beam 127 870


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 233)
node 871 20000 9000 7900
rigidLink beam 114 871
# Geometric transformation command
geomTransf PDelta 233 1.0 0.0 -0.0
element forceBeamColumn 233 870 871 233 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 120), with Mesh Node = 126 (auxiliary for element 234)
node 872 20000 14500 11600
rigidLink beam 126 872


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 122), with Mesh Node = 128 (auxiliary for element 234)
node 873 20000 14500 14500
rigidLink beam 128 873
# Geometric transformation command
geomTransf PDelta 234 1.0 0.0 -0.0
element forceBeamColumn 234 872 873 234 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 235)
node 874 20000 9000 11600
rigidLink beam 125 874


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 235)
node 875 20000 9000 14500
rigidLink beam 124 875
# Geometric transformation command
geomTransf PDelta 235 1.0 0.0 -0.0
element forceBeamColumn 235 874 875 235 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 236)
node 876 12000 14500 14900
rigidLink beam 98 876


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 123), with Mesh Node = 129 (auxiliary for element 236)
node 877 12000 14500 17800
rigidLink beam 129 877
# Geometric transformation command
geomTransf PDelta 236 1.0 0.0 -0.0
element forceBeamColumn 236 876 877 236 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 124), with Mesh Node = 130 (auxiliary for element 237)
node 878 20000 14500 5000
rigidLink beam 130 878


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 105), with Mesh Node = 111 (auxiliary for element 237)
node 879 20000 14500 7900
rigidLink beam 111 879
# Geometric transformation command
geomTransf PDelta 237 1.0 0.0 -0.0
element forceBeamColumn 237 878 879 237 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 238)
node 880 19800 0 14700
rigidLink beam 218 880


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 125), with Mesh Node = 131 (auxiliary for element 238)
node 881 16200 0 14700
rigidLink beam 249 881

# Extra nodes for zeroLength
# node tag x y z
node 882 19800 0 14700
node 883 16200 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 238 0.0 0.0 1.0
element elasticBeamColumn 238 882 883 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 238

# zero_length_elements zeroLength
element zeroLength 1100 880 882 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1101 883 881 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 126), with Mesh Node = 132 (auxiliary for element 239)
node 884 12000 200 14700
rigidLink beam 250 884


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 239)
node 885 12000 5300 14700
rigidLink beam 201 885

# Extra nodes for zeroLength
# node tag x y z
node 886 12000 200 14700
node 887 12000 5300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 239 0.0 -0.0 1.0
element elasticBeamColumn 239 886 887 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 239

# zero_length_elements zeroLength
element zeroLength 1102 884 886 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1103 887 885 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 126), with Mesh Node = 132 (auxiliary for element 240)
node 888 12200 0 14700
rigidLink beam 250 888


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 125), with Mesh Node = 131 (auxiliary for element 240)
node 889 15800 0 14700
rigidLink beam 249 889

# Extra nodes for zeroLength
# node tag x y z
node 890 12200 0 14700
node 891 15800 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 240 0.0 0.0 1.0
element elasticBeamColumn 240 890 891 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 240

# zero_length_elements zeroLength
element zeroLength 1104 888 890 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1105 891 889 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 125), with Mesh Node = 131 (auxiliary for element 241)
node 892 16000 200 14700
rigidLink beam 249 892

# Extra nodes for zeroLength
# node tag x y z
node 893 16000 200 14700
node 894 16000 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 241 0.0 -0.0 1.0
element elasticBeamColumn 241 893 894 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 241

# zero_length_elements zeroLength
element zeroLength 1106 892 893 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1107 894 7 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 122), with Mesh Node = 128 (auxiliary for element 242)
node 895 20000 14500 14900
rigidLink beam 128 895


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 98), with Mesh Node = 104 (auxiliary for element 242)
node 896 20000 14500 17800
rigidLink beam 104 896
# Geometric transformation command
geomTransf PDelta 242 1.0 0.0 -0.0
element forceBeamColumn 242 895 896 242 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 127), with Mesh Node = 133 (auxiliary for element 243)
node 897 12000 200 18000
rigidLink beam 251 897

# Extra nodes for zeroLength
# node tag x y z
node 898 12000 200 18000
node 899 12000 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 243 0.0 -0.0 1.0
element elasticBeamColumn 243 898 899 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 243

# zero_length_elements zeroLength
element zeroLength 1108 897 898 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1109 899 9 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 244)
node 900 12000 0 11600
rigidLink beam 56 900


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 126), with Mesh Node = 132 (auxiliary for element 244)
node 901 12000 0 14500
rigidLink beam 132 901
# Geometric transformation command
geomTransf PDelta 244 1.0 0.0 -0.0
element forceBeamColumn 244 900 901 244 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 245)
node 902 16000 5300 18000
rigidLink beam 224 902

# Extra nodes for zeroLength
# node tag x y z
node 903 16000 0 18000
node 904 16000 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 245 0.0 -0.0 1.0
element elasticBeamColumn 245 903 904 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 245

# zero_length_elements zeroLength
element zeroLength 1110 6 903 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1111 904 902 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 246)
node 905 16000 5500 17800
rigidLink beam 106 905
# Geometric transformation command
geomTransf PDelta 246 1.0 0.0 -0.0
element forceBeamColumn 246 7 905 246 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 127), with Mesh Node = 133 (auxiliary for element 247)
node 906 12200 0 18000
rigidLink beam 251 906

# Extra nodes for zeroLength
# node tag x y z
node 907 12200 0 18000
node 908 16000 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 247 0.0 0.0 1.0
element elasticBeamColumn 247 907 908 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 247

# zero_length_elements zeroLength
element zeroLength 1112 906 907 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1113 908 6 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 126), with Mesh Node = 132 (auxiliary for element 248)
node 909 12000 0 14900
rigidLink beam 132 909


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 127), with Mesh Node = 133 (auxiliary for element 248)
node 910 12000 0 17800
rigidLink beam 133 910
# Geometric transformation command
geomTransf PDelta 248 1.0 0.0 -0.0
element forceBeamColumn 248 909 910 248 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 128), with Mesh Node = 134 (auxiliary for element 249)
node 911 19800 0 18000
rigidLink beam 252 911

# Extra nodes for zeroLength
# node tag x y z
node 912 16000 0 18000
node 913 19800 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 249 0.0 0.0 1.0
element elasticBeamColumn 249 912 913 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 249

# zero_length_elements zeroLength
element zeroLength 1114 6 912 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1115 913 911 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 107), with Mesh Node = 113 (auxiliary for element 250)
node 914 8200 0 18000
rigidLink beam 231 914


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 127), with Mesh Node = 133 (auxiliary for element 250)
node 915 11800 0 18000
rigidLink beam 251 915

# Extra nodes for zeroLength
# node tag x y z
node 916 8200 0 18000
node 917 11800 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 250 0.0 0.0 1.0
element elasticBeamColumn 250 916 917 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 250

# zero_length_elements zeroLength
element zeroLength 1116 914 916 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1117 917 915 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 251)
node 918 8200 0 14700
rigidLink beam 191 918


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 126), with Mesh Node = 132 (auxiliary for element 251)
node 919 11800 0 14700
rigidLink beam 250 919

# Extra nodes for zeroLength
# node tag x y z
node 920 8200 0 14700
node 921 11800 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 251 0.0 0.0 1.0
element elasticBeamColumn 251 920 921 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 251

# zero_length_elements zeroLength
element zeroLength 1118 918 920 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1119 921 919 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 53), with Mesh Node = 59 (auxiliary for element 252)
node 922 16000 0 11600
rigidLink beam 59 922


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 125), with Mesh Node = 131 (auxiliary for element 252)
node 923 16000 0 14500
rigidLink beam 131 923
# Geometric transformation command
geomTransf PDelta 252 1.0 0.0 -0.0
element forceBeamColumn 252 922 923 252 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 253)
node 924 20000 9200 11400
rigidLink beam 243 924


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 120), with Mesh Node = 126 (auxiliary for element 253)
node 925 20000 14300 11400
rigidLink beam 244 925

# Extra nodes for zeroLength
# node tag x y z
node 926 20000 9200 11400
node 927 20000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 253 0.0 -0.0 1.0
element elasticBeamColumn 253 926 927 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 253

# zero_length_elements zeroLength
element zeroLength 1120 924 926 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1121 927 925 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 254)
node 928 16000 9200 11400
rigidLink beam 187 928


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 51), with Mesh Node = 57 (auxiliary for element 254)
node 929 16000 14300 11400
rigidLink beam 184 929

# Extra nodes for zeroLength
# node tag x y z
node 930 16000 9200 11400
node 931 16000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 254 0.0 -0.0 1.0
element elasticBeamColumn 254 930 931 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 254

# zero_length_elements zeroLength
element zeroLength 1122 928 930 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1123 931 929 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 129), with Mesh Node = 135 (auxiliary for element 255)
node 932 16200 14500 4800
rigidLink beam 253 932


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 124), with Mesh Node = 130 (auxiliary for element 255)
node 933 19800 14500 4800
rigidLink beam 248 933

# Extra nodes for zeroLength
# node tag x y z
node 934 16200 14500 4800
node 935 19800 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 255 0.0 0.0 1.0
element elasticBeamColumn 255 934 935 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 255

# zero_length_elements zeroLength
element zeroLength 1124 932 934 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1125 935 933 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 35), with Mesh Node = 41 (auxiliary for element 256)
node 936 12000 0 4600
rigidLink beam 41 936
# Geometric transformation command
geomTransf PDelta 256 1.0 0.0 -0.0
element forceBeamColumn 256 136 936 256 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 257)
node 937 20000 0 4600
rigidLink beam 92 937
# Geometric transformation command
geomTransf PDelta 257 1.0 0.0 -0.0
element forceBeamColumn 257 137 937 257 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 125), with Mesh Node = 131 (auxiliary for element 258)
node 938 16000 0 14900
rigidLink beam 131 938
# Geometric transformation command
geomTransf PDelta 258 1.0 0.0 -0.0
element forceBeamColumn 258 938 6 258 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 34), with Mesh Node = 40 (auxiliary for element 259)
node 939 8000 0 4600
rigidLink beam 40 939
# Geometric transformation command
geomTransf PDelta 259 1.0 0.0 -0.0
element forceBeamColumn 259 138 939 259 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 260 1.0 0.0 -0.0
element forceBeamColumn 260 139 18 260 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 36), with Mesh Node = 42 (auxiliary for element 261)
node 940 16000 0 4600
rigidLink beam 42 940
# Geometric transformation command
geomTransf PDelta 261 1.0 0.0 -0.0
element forceBeamColumn 261 140 940 261 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 262)
node 941 4200 14500 4800
rigidLink beam 196 941


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 262)
node 942 7800 14500 4800
rigidLink beam 212 942

# Extra nodes for zeroLength
# node tag x y z
node 943 4200 14500 4800
node 944 7800 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 262 0.0 0.0 1.0
element elasticBeamColumn 262 943 944 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 262

# zero_length_elements zeroLength
element zeroLength 1126 941 943 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1127 944 942 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 115), with Mesh Node = 121 (auxiliary for element 263)
node 945 0 200 11400
rigidLink beam 239 945


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 39), with Mesh Node = 45 (auxiliary for element 263)
node 946 0 5300 11400
rigidLink beam 172 946

# Extra nodes for zeroLength
# node tag x y z
node 947 0 200 11400
node 948 0 5300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 263 0.0 -0.0 1.0
element elasticBeamColumn 263 947 948 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 263

# zero_length_elements zeroLength
element zeroLength 1128 945 947 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1129 948 946 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 115), with Mesh Node = 121 (auxiliary for element 264)
node 949 200 0 11400
rigidLink beam 239 949


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 264)
node 950 3800 0 11400
rigidLink beam 182 950

# Extra nodes for zeroLength
# node tag x y z
node 951 200 0 11400
node 952 3800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 264 0.0 0.0 1.0
element elasticBeamColumn 264 951 952 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 264

# zero_length_elements zeroLength
element zeroLength 1130 949 951 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1131 952 950 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 265)
node 953 4200 14500 11400
rigidLink beam 193 953


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 265)
node 954 7800 14500 11400
rigidLink beam 188 954

# Extra nodes for zeroLength
# node tag x y z
node 955 4200 14500 11400
node 956 7800 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 265 0.0 0.0 1.0
element elasticBeamColumn 265 955 956 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 265

# zero_length_elements zeroLength
element zeroLength 1132 953 955 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1133 956 954 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 266)
node 957 4000 0 14900
rigidLink beam 63 957


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 135), with Mesh Node = 141 (auxiliary for element 266)
node 958 4000 0 17800
rigidLink beam 141 958
# Geometric transformation command
geomTransf PDelta 266 1.0 0.0 -0.0
element forceBeamColumn 266 957 958 266 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 267)
node 959 4000 5700 18000
rigidLink beam 238 959


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 267)
node 960 4000 8800 18000
rigidLink beam 205 960

# Extra nodes for zeroLength
# node tag x y z
node 961 4000 5700 18000
node 962 4000 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 267 0.0 -0.0 1.0
element elasticBeamColumn 267 961 962 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 267

# zero_length_elements zeroLength
element zeroLength 1134 959 961 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1135 962 960 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 116), with Mesh Node = 122 (auxiliary for element 268)
node 963 0 200 18000
rigidLink beam 240 963


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 268)
node 964 0 5300 18000
rigidLink beam 241 964

# Extra nodes for zeroLength
# node tag x y z
node 965 0 200 18000
node 966 0 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 268 0.0 -0.0 1.0
element elasticBeamColumn 268 965 966 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 268

# zero_length_elements zeroLength
element zeroLength 1136 963 965 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1137 966 964 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 269)
node 967 0 5700 18000
rigidLink beam 241 967


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 269)
node 968 0 8800 18000
rigidLink beam 207 968

# Extra nodes for zeroLength
# node tag x y z
node 969 0 5700 18000
node 970 0 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 269 0.0 -0.0 1.0
element elasticBeamColumn 269 969 970 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 269

# zero_length_elements zeroLength
element zeroLength 1138 967 969 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1139 970 968 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 270)
node 971 200 5500 18000
rigidLink beam 241 971


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 270)
node 972 3800 5500 18000
rigidLink beam 238 972

# Extra nodes for zeroLength
# node tag x y z
node 973 200 5500 18000
node 974 3800 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 270 0.0 0.0 1.0
element elasticBeamColumn 270 973 974 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 270

# zero_length_elements zeroLength
element zeroLength 1140 971 973 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1141 974 972 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 45), with Mesh Node = 51 (auxiliary for element 271)
node 975 0 200 8100
rigidLink beam 178 975

# Extra nodes for zeroLength
# node tag x y z
node 976 0 200 8100
node 977 0 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 271 0.0 -0.0 1.0
element elasticBeamColumn 271 976 977 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 271

# zero_length_elements zeroLength
element zeroLength 1142 975 976 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1143 977 17 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 43), with Mesh Node = 49 (auxiliary for element 272)
node 978 0 8800 8100
rigidLink beam 176 978

# Extra nodes for zeroLength
# node tag x y z
node 979 0 5500 8100
node 980 0 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 272 0.0 -0.0 1.0
element elasticBeamColumn 272 979 980 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 272

# zero_length_elements zeroLength
element zeroLength 1144 17 979 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1145 980 978 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 48), with Mesh Node = 54 (auxiliary for element 273)
node 981 0 14500 11600
rigidLink beam 54 981


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 273)
node 982 0 14500 14500
rigidLink beam 71 982
# Geometric transformation command
geomTransf PDelta 273 1.0 0.0 -0.0
element forceBeamColumn 273 981 982 273 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 274)
node 983 0 9000 11600
rigidLink beam 91 983


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 274)
node 984 0 9000 14500
rigidLink beam 67 984
# Geometric transformation command
geomTransf PDelta 274 1.0 0.0 -0.0
element forceBeamColumn 274 983 984 274 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 275)
node 985 4000 0 11600
rigidLink beam 55 985


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 275)
node 986 4000 0 14500
rigidLink beam 63 986
# Geometric transformation command
geomTransf PDelta 275 1.0 0.0 -0.0
element forceBeamColumn 275 985 986 275 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 276)
node 987 20000 0 5000
rigidLink beam 92 987


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 112), with Mesh Node = 118 (auxiliary for element 276)
node 988 20000 0 7900
rigidLink beam 118 988
# Geometric transformation command
geomTransf PDelta 276 1.0 0.0 -0.0
element forceBeamColumn 276 987 988 276 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 51), with Mesh Node = 57 (auxiliary for element 277)
node 989 16200 14500 11400
rigidLink beam 184 989


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 120), with Mesh Node = 126 (auxiliary for element 277)
node 990 19800 14500 11400
rigidLink beam 244 990

# Extra nodes for zeroLength
# node tag x y z
node 991 16200 14500 11400
node 992 19800 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 277 0.0 0.0 1.0
element elasticBeamColumn 277 991 992 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 277

# zero_length_elements zeroLength
element zeroLength 1146 989 991 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1147 992 990 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 278)
node 993 16200 9000 11400
rigidLink beam 187 993


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 278)
node 994 19800 9000 11400
rigidLink beam 243 994

# Extra nodes for zeroLength
# node tag x y z
node 995 16200 9000 11400
node 996 19800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 278 0.0 0.0 1.0
element elasticBeamColumn 278 995 996 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 278

# zero_length_elements zeroLength
element zeroLength 1148 993 995 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1149 996 994 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 279)
node 997 12200 9000 4800
rigidLink beam 200 997


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 279)
node 998 15800 9000 4800
rigidLink beam 234 998

# Extra nodes for zeroLength
# node tag x y z
node 999 12200 9000 4800
node 1000 15800 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 279 0.0 0.0 1.0
element elasticBeamColumn 279 999 1000 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 279

# zero_length_elements zeroLength
element zeroLength 1150 997 999 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1151 1000 998 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 280)
node 1001 16000 9200 4800
rigidLink beam 234 1001


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 129), with Mesh Node = 135 (auxiliary for element 280)
node 1002 16000 14300 4800
rigidLink beam 253 1002

# Extra nodes for zeroLength
# node tag x y z
node 1003 16000 9200 4800
node 1004 16000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 280 0.0 -0.0 1.0
element elasticBeamColumn 280 1003 1004 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 280

# zero_length_elements zeroLength
element zeroLength 1152 1001 1003 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1153 1004 1002 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 281)
node 1005 8200 14500 4800
rigidLink beam 212 1005


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 281)
node 1006 11800 14500 4800
rigidLink beam 213 1006

# Extra nodes for zeroLength
# node tag x y z
node 1007 8200 14500 4800
node 1008 11800 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 281 0.0 0.0 1.0
element elasticBeamColumn 281 1007 1008 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 281

# zero_length_elements zeroLength
element zeroLength 1154 1005 1007 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1155 1008 1006 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 121), with Mesh Node = 127 (auxiliary for element 282)
node 1009 20000 8800 4800
rigidLink beam 245 1009

# Extra nodes for zeroLength
# node tag x y z
node 1010 20000 5500 4800
node 1011 20000 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 282 0.0 -0.0 1.0
element elasticBeamColumn 282 1010 1011 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 282

# zero_length_elements zeroLength
element zeroLength 1156 18 1010 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1157 1011 1009 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 87), with Mesh Node = 93 (auxiliary for element 283)
node 1012 16000 5700 4800
rigidLink beam 211 1012


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 283)
node 1013 16000 8800 4800
rigidLink beam 234 1013

# Extra nodes for zeroLength
# node tag x y z
node 1014 16000 5700 4800
node 1015 16000 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 283 0.0 -0.0 1.0
element elasticBeamColumn 283 1014 1015 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 283

# zero_length_elements zeroLength
element zeroLength 1158 1012 1014 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1159 1015 1013 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 284)
node 1016 12200 14500 4800
rigidLink beam 213 1016


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 129), with Mesh Node = 135 (auxiliary for element 284)
node 1017 15800 14500 4800
rigidLink beam 253 1017

# Extra nodes for zeroLength
# node tag x y z
node 1018 12200 14500 4800
node 1019 15800 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 284 0.0 0.0 1.0
element elasticBeamColumn 284 1018 1019 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 284

# zero_length_elements zeroLength
element zeroLength 1160 1016 1018 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1161 1019 1017 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 285)
node 1020 16200 9000 4800
rigidLink beam 234 1020


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 121), with Mesh Node = 127 (auxiliary for element 285)
node 1021 19800 9000 4800
rigidLink beam 245 1021

# Extra nodes for zeroLength
# node tag x y z
node 1022 16200 9000 4800
node 1023 19800 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 285 0.0 0.0 1.0
element elasticBeamColumn 285 1022 1023 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 285

# zero_length_elements zeroLength
element zeroLength 1162 1020 1022 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1163 1023 1021 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 286)
node 1024 16200 9000 14700
rigidLink beam 235 1024


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 286)
node 1025 19800 9000 14700
rigidLink beam 242 1025

# Extra nodes for zeroLength
# node tag x y z
node 1026 16200 9000 14700
node 1027 19800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 286 0.0 0.0 1.0
element elasticBeamColumn 286 1026 1027 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 286

# zero_length_elements zeroLength
element zeroLength 1164 1024 1026 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1165 1027 1025 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 287)
node 1028 12200 14500 14700
rigidLink beam 216 1028


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 287)
node 1029 15800 14500 14700
rigidLink beam 220 1029

# Extra nodes for zeroLength
# node tag x y z
node 1030 12200 14500 14700
node 1031 15800 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 287 0.0 0.0 1.0
element elasticBeamColumn 287 1030 1031 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 287

# zero_length_elements zeroLength
element zeroLength 1166 1028 1030 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1167 1031 1029 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 288)
node 1032 8200 14500 14700
rigidLink beam 203 1032


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 288)
node 1033 11800 14500 14700
rigidLink beam 216 1033

# Extra nodes for zeroLength
# node tag x y z
node 1034 8200 14500 14700
node 1035 11800 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 288 0.0 0.0 1.0
element elasticBeamColumn 288 1034 1035 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 288

# zero_length_elements zeroLength
element zeroLength 1168 1032 1034 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1169 1035 1033 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 289)
node 1036 16200 14500 14700
rigidLink beam 220 1036


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 122), with Mesh Node = 128 (auxiliary for element 289)
node 1037 19800 14500 14700
rigidLink beam 246 1037

# Extra nodes for zeroLength
# node tag x y z
node 1038 16200 14500 14700
node 1039 19800 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 289 0.0 0.0 1.0
element elasticBeamColumn 289 1038 1039 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 289

# zero_length_elements zeroLength
element zeroLength 1170 1036 1038 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1171 1039 1037 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 290)
node 1040 8000 8800 14700
rigidLink beam 199 1040

# Extra nodes for zeroLength
# node tag x y z
node 1041 8000 5500 14700
node 1042 8000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 290 0.0 -0.0 1.0
element elasticBeamColumn 290 1041 1042 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 290

# zero_length_elements zeroLength
element zeroLength 1172 12 1041 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1173 1042 1040 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 121), with Mesh Node = 127 (auxiliary for element 291)
node 1043 20000 9200 4800
rigidLink beam 245 1043


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 124), with Mesh Node = 130 (auxiliary for element 291)
node 1044 20000 14300 4800
rigidLink beam 248 1044

# Extra nodes for zeroLength
# node tag x y z
node 1045 20000 9200 4800
node 1046 20000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 291 0.0 -0.0 1.0
element elasticBeamColumn 291 1045 1046 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 291

# zero_length_elements zeroLength
element zeroLength 1174 1043 1045 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1175 1046 1044 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 292)
node 1047 12200 9000 14700
rigidLink beam 214 1047


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 292)
node 1048 15800 9000 14700
rigidLink beam 235 1048

# Extra nodes for zeroLength
# node tag x y z
node 1049 12200 9000 14700
node 1050 15800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 292 0.0 0.0 1.0
element elasticBeamColumn 292 1049 1050 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 292

# zero_length_elements zeroLength
element zeroLength 1176 1047 1049 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1177 1050 1048 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 293)
node 1051 8000 9200 14700
rigidLink beam 199 1051


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 293)
node 1052 8000 14300 14700
rigidLink beam 203 1052

# Extra nodes for zeroLength
# node tag x y z
node 1053 8000 9200 14700
node 1054 8000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 293 0.0 -0.0 1.0
element elasticBeamColumn 293 1053 1054 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 293

# zero_length_elements zeroLength
element zeroLength 1178 1051 1053 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1179 1054 1052 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 294)
node 1055 8200 9000 14700
rigidLink beam 199 1055


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 294)
node 1056 11800 9000 14700
rigidLink beam 214 1056

# Extra nodes for zeroLength
# node tag x y z
node 1057 8200 9000 14700
node 1058 11800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 294 0.0 0.0 1.0
element elasticBeamColumn 294 1057 1058 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 294

# zero_length_elements zeroLength
element zeroLength 1180 1055 1057 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1181 1058 1056 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 129), with Mesh Node = 135 (auxiliary for element 295)
node 1059 16000 14500 5000
rigidLink beam 135 1059


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 295)
node 1060 16000 14500 7900
rigidLink beam 101 1060
# Geometric transformation command
geomTransf PDelta 295 1.0 0.0 -0.0
element forceBeamColumn 295 1059 1060 295 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 84), with Mesh Node = 90 (auxiliary for element 296)
node 1061 8200 14500 18000
rigidLink beam 208 1061


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 123), with Mesh Node = 129 (auxiliary for element 296)
node 1062 11800 14500 18000
rigidLink beam 247 1062

# Extra nodes for zeroLength
# node tag x y z
node 1063 8200 14500 18000
node 1064 11800 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 296 0.0 0.0 1.0
element elasticBeamColumn 296 1063 1064 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 296

# zero_length_elements zeroLength
element zeroLength 1182 1061 1063 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1183 1064 1062 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 102), with Mesh Node = 108 (auxiliary for element 297)
node 1065 19800 9000 18000
rigidLink beam 226 1065

# Extra nodes for zeroLength
# node tag x y z
node 1066 16000 9000 18000
node 1067 19800 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 297 0.0 0.0 1.0
element elasticBeamColumn 297 1066 1067 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 297

# zero_length_elements zeroLength
element zeroLength 1184 8 1066 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1185 1067 1065 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 298)
node 1068 8200 9000 18000
rigidLink beam 237 1068


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 298)
node 1069 11800 9000 18000
rigidLink beam 225 1069

# Extra nodes for zeroLength
# node tag x y z
node 1070 8200 9000 18000
node 1071 11800 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 298 0.0 0.0 1.0
element elasticBeamColumn 298 1070 1071 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 298

# zero_length_elements zeroLength
element zeroLength 1186 1068 1070 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1187 1071 1069 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 299)
node 1072 8000 5700 18000
rigidLink beam 223 1072


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 299)
node 1073 8000 8800 18000
rigidLink beam 237 1073

# Extra nodes for zeroLength
# node tag x y z
node 1074 8000 5700 18000
node 1075 8000 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 299 0.0 -0.0 1.0
element elasticBeamColumn 299 1074 1075 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 299

# zero_length_elements zeroLength
element zeroLength 1188 1072 1074 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1189 1075 1073 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 300)
node 1076 12200 9000 18000
rigidLink beam 225 1076

# Extra nodes for zeroLength
# node tag x y z
node 1077 12200 9000 18000
node 1078 16000 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 300 0.0 0.0 1.0
element elasticBeamColumn 300 1077 1078 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 300

# zero_length_elements zeroLength
element zeroLength 1190 1076 1077 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1191 1078 8 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 301)
node 1079 8000 9200 18000
rigidLink beam 237 1079


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 84), with Mesh Node = 90 (auxiliary for element 301)
node 1080 8000 14300 18000
rigidLink beam 208 1080

# Extra nodes for zeroLength
# node tag x y z
node 1081 8000 9200 18000
node 1082 8000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 301 0.0 -0.0 1.0
element elasticBeamColumn 301 1081 1082 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 301

# zero_length_elements zeroLength
element zeroLength 1192 1079 1081 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1193 1082 1080 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 135), with Mesh Node = 141 (auxiliary for element 302)
node 1083 4200 0 18000
rigidLink beam 254 1083


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 107), with Mesh Node = 113 (auxiliary for element 302)
node 1084 7800 0 18000
rigidLink beam 231 1084

# Extra nodes for zeroLength
# node tag x y z
node 1085 4200 0 18000
node 1086 7800 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 302 0.0 0.0 1.0
element elasticBeamColumn 302 1085 1086 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 302

# zero_length_elements zeroLength
element zeroLength 1194 1083 1085 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1195 1086 1084 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 303)
node 1087 4200 5500 18000
rigidLink beam 238 1087


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 303)
node 1088 7800 5500 18000
rigidLink beam 223 1088

# Extra nodes for zeroLength
# node tag x y z
node 1089 4200 5500 18000
node 1090 7800 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 303 0.0 0.0 1.0
element elasticBeamColumn 303 1089 1090 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 303

# zero_length_elements zeroLength
element zeroLength 1196 1087 1089 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1197 1090 1088 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 304)
node 1091 12000 9000 4600
rigidLink beam 82 1091
# Geometric transformation command
geomTransf PDelta 304 1.0 0.0 -0.0
element forceBeamColumn 304 142 1091 304 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 87), with Mesh Node = 93 (auxiliary for element 305)
node 1092 16000 5500 4600
rigidLink beam 93 1092
# Geometric transformation command
geomTransf PDelta 305 1.0 0.0 -0.0
element forceBeamColumn 305 143 1092 305 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 306)
node 1093 12000 14500 4600
rigidLink beam 95 1093
# Geometric transformation command
geomTransf PDelta 306 1.0 0.0 -0.0
element forceBeamColumn 306 144 1093 306 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 129), with Mesh Node = 135 (auxiliary for element 307)
node 1094 16000 14500 4600
rigidLink beam 135 1094
# Geometric transformation command
geomTransf PDelta 307 1.0 0.0 -0.0
element forceBeamColumn 307 145 1094 307 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 121), with Mesh Node = 127 (auxiliary for element 308)
node 1095 20000 9000 4600
rigidLink beam 127 1095
# Geometric transformation command
geomTransf PDelta 308 1.0 0.0 -0.0
element forceBeamColumn 308 146 1095 308 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 309)
node 1096 16000 9000 4600
rigidLink beam 116 1096
# Geometric transformation command
geomTransf PDelta 309 1.0 0.0 -0.0
element forceBeamColumn 309 147 1096 309 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 310)
node 1097 8000 14500 4600
rigidLink beam 94 1097
# Geometric transformation command
geomTransf PDelta 310 1.0 0.0 -0.0
element forceBeamColumn 310 148 1097 310 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 124), with Mesh Node = 130 (auxiliary for element 311)
node 1098 20000 14500 4600
rigidLink beam 130 1098
# Geometric transformation command
geomTransf PDelta 311 1.0 0.0 -0.0
element forceBeamColumn 311 149 1098 311 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 312)
node 1099 20000 5500 8300
rigidLink beam 115 1099
# Geometric transformation command
geomTransf PDelta 312 1.0 0.0 -0.0
element forceBeamColumn 312 1099 10 312 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 313)
node 1100 16000 5500 11200
rigidLink beam 84 1100
# Geometric transformation command
geomTransf PDelta 313 1.0 0.0 -0.0
element forceBeamColumn 313 15 1100 313 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 112), with Mesh Node = 118 (auxiliary for element 314)
node 1101 20000 0 8300
rigidLink beam 118 1101


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 314)
node 1102 20000 0 11200
rigidLink beam 97 1102
# Geometric transformation command
geomTransf PDelta 314 1.0 0.0 -0.0
element forceBeamColumn 314 1101 1102 314 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 315)
node 1103 16000 5500 11600
rigidLink beam 84 1103
# Geometric transformation command
geomTransf PDelta 315 1.0 0.0 -0.0
element forceBeamColumn 315 1103 7 315 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 316)
node 1104 20000 0 11600
rigidLink beam 97 1104


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 316)
node 1105 20000 0 14500
rigidLink beam 100 1105
# Geometric transformation command
geomTransf PDelta 316 1.0 0.0 -0.0
element forceBeamColumn 316 1104 1105 316 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 317)
node 1106 20000 0 14900
rigidLink beam 100 1106


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 128), with Mesh Node = 134 (auxiliary for element 317)
node 1107 20000 0 17800
rigidLink beam 134 1107
# Geometric transformation command
geomTransf PDelta 317 1.0 0.0 -0.0
element forceBeamColumn 317 1106 1107 317 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 318)
node 1108 20000 200 11400
rigidLink beam 215 1108

# Extra nodes for zeroLength
# node tag x y z
node 1109 20000 200 11400
node 1110 20000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 318 0.0 -0.0 1.0
element elasticBeamColumn 318 1109 1110 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 318

# zero_length_elements zeroLength
element zeroLength 1198 1108 1109 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1199 1110 10 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 319)
node 1111 20000 8800 11400
rigidLink beam 243 1111

# Extra nodes for zeroLength
# node tag x y z
node 1112 20000 5500 11400
node 1113 20000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 319 0.0 -0.0 1.0
element elasticBeamColumn 319 1112 1113 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 319

# zero_length_elements zeroLength
element zeroLength 1200 10 1112 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1201 1113 1111 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 116), with Mesh Node = 122 (auxiliary for element 320)
node 1114 200 0 18000
rigidLink beam 240 1114


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 135), with Mesh Node = 141 (auxiliary for element 320)
node 1115 3800 0 18000
rigidLink beam 254 1115

# Extra nodes for zeroLength
# node tag x y z
node 1116 200 0 18000
node 1117 3800 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 320 0.0 0.0 1.0
element elasticBeamColumn 320 1116 1117 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 320

# zero_length_elements zeroLength
element zeroLength 1202 1114 1116 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1203 1117 1115 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 321)
node 1118 16000 9200 14700
rigidLink beam 235 1118


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 321)
node 1119 16000 14300 14700
rigidLink beam 220 1119

# Extra nodes for zeroLength
# node tag x y z
node 1120 16000 9200 14700
node 1121 16000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 321 0.0 -0.0 1.0
element elasticBeamColumn 321 1120 1121 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 321

# zero_length_elements zeroLength
element zeroLength 1204 1118 1120 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1205 1121 1119 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 322)
node 1122 16000 8800 14700
rigidLink beam 235 1122

# Extra nodes for zeroLength
# node tag x y z
node 1123 16000 5500 14700
node 1124 16000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 322 0.0 -0.0 1.0
element elasticBeamColumn 322 1123 1124 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 322

# zero_length_elements zeroLength
element zeroLength 1206 7 1123 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1207 1124 1122 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 93), with Mesh Node = 99 (auxiliary for element 323)
node 1125 20000 5700 14700
rigidLink beam 217 1125


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 323)
node 1126 20000 8800 14700
rigidLink beam 242 1126

# Extra nodes for zeroLength
# node tag x y z
node 1127 20000 5700 14700
node 1128 20000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 323 0.0 -0.0 1.0
element elasticBeamColumn 323 1127 1128 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 323

# zero_length_elements zeroLength
element zeroLength 1208 1125 1127 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1209 1128 1126 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 324)
node 1129 20000 9200 14700
rigidLink beam 242 1129


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 122), with Mesh Node = 128 (auxiliary for element 324)
node 1130 20000 14300 14700
rigidLink beam 246 1130

# Extra nodes for zeroLength
# node tag x y z
node 1131 20000 9200 14700
node 1132 20000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 324 0.0 -0.0 1.0
element elasticBeamColumn 324 1131 1132 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 324

# zero_length_elements zeroLength
element zeroLength 1210 1129 1131 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1211 1132 1130 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 123), with Mesh Node = 129 (auxiliary for element 325)
node 1133 12200 14500 18000
rigidLink beam 247 1133


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 325)
node 1134 15800 14500 18000
rigidLink beam 221 1134

# Extra nodes for zeroLength
# node tag x y z
node 1135 12200 14500 18000
node 1136 15800 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 325 0.0 0.0 1.0
element elasticBeamColumn 325 1135 1136 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 325

# zero_length_elements zeroLength
element zeroLength 1212 1133 1135 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1213 1136 1134 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 326)
node 1137 12000 9200 18000
rigidLink beam 225 1137


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 123), with Mesh Node = 129 (auxiliary for element 326)
node 1138 12000 14300 18000
rigidLink beam 247 1138

# Extra nodes for zeroLength
# node tag x y z
node 1139 12000 9200 18000
node 1140 12000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 326 0.0 -0.0 1.0
element elasticBeamColumn 326 1139 1140 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 326

# zero_length_elements zeroLength
element zeroLength 1214 1137 1139 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1215 1140 1138 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 128), with Mesh Node = 134 (auxiliary for element 327)
node 1141 20000 200 18000
rigidLink beam 252 1141


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 104), with Mesh Node = 110 (auxiliary for element 327)
node 1142 20000 5300 18000
rigidLink beam 228 1142

# Extra nodes for zeroLength
# node tag x y z
node 1143 20000 200 18000
node 1144 20000 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 327 0.0 -0.0 1.0
element elasticBeamColumn 327 1143 1144 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 327

# zero_length_elements zeroLength
element zeroLength 1216 1141 1143 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1217 1144 1142 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 135), with Mesh Node = 141 (auxiliary for element 328)
node 1145 4000 200 18000
rigidLink beam 254 1145


# RCJointModel3D at Geometry = 1058 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 328)
node 1146 4000 5300 18000
rigidLink beam 238 1146

# Extra nodes for zeroLength
# node tag x y z
node 1147 4000 200 18000
node 1148 4000 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 328 0.0 -0.0 1.0
element elasticBeamColumn 328 1147 1148 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 328

# zero_length_elements zeroLength
element zeroLength 1218 1145 1147 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1219 1148 1146 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# truss_elements truss
element truss 329 15 116 1.0 85
element truss 330 83 33 1.0 85
element truss 331 96 11 1.0 85
element truss 332 33 26 1.0 85
element truss 333 26 82 1.0 85
element truss 334 28 19 1.0 85
element truss 335 11 28 1.0 85
element truss 336 8 102 1.0 82
element truss 337 103 117 1.0 82
element truss 338 132 11 1.0 82
element truss 339 107 98 1.0 82
element truss 340 83 56 1.0 82
element truss 341 33 109 1.0 82
element truss 342 129 96 1.0 82
element truss 343 96 34 1.0 82
element truss 344 98 33 1.0 82
element truss 345 34 28 1.0 82
element truss 346 131 84 1.0 82
element truss 347 56 26 1.0 82
element truss 348 26 41 1.0 82
element truss 349 11 31 1.0 82
element truss 350 31 19 1.0 82
element truss 351 109 82 1.0 82
element truss 352 28 95 1.0 82
element truss 353 102 60 1.0 82
element truss 354 117 57 1.0 82
element truss 355 84 47 1.0 82
element truss 356 60 101 1.0 82
element truss 357 59 15 1.0 82
element truss 358 7 59 1.0 82
element truss 359 47 93 1.0 82
element truss 360 15 42 1.0 82
element truss 361 57 112 1.0 82
element truss 362 101 116 1.0 82
element truss 363 112 135 1.0 82
element truss 364 107 117 1.0 72
element truss 365 119 96 1.0 72
element truss 366 107 72 1.0 72
element truss 367 110 7 1.0 72
element truss 368 51 39 1.0 76
element truss 369 17 37 1.0 76
element truss 370 49 53 1.0 76
element truss 371 121 17 1.0 76
element truss 372 45 51 1.0 76
element truss 373 50 52 1.0 76
element truss 374 7 60 1.0 85
element truss 375 49 38 1.0 72
element truss 376 99 106 1.0 72
element truss 377 56 47 1.0 70
element truss 378 31 59 1.0 70
element truss 379 30 56 1.0 70
element truss 380 59 118 1.0 70
element truss 381 62 31 1.0 70
element truss 382 45 49 1.0 79
element truss 383 10 124 1.0 79
element truss 384 10 114 1.0 79
element truss 385 49 39 1.0 79
element truss 386 17 52 1.0 79
element truss 387 91 17 1.0 79
element truss 388 115 127 1.0 79
element truss 389 115 125 1.0 79
element truss 390 32 44 1.0 85
element truss 391 18 114 1.0 79
element truss 392 67 45 1.0 79
element truss 393 99 125 1.0 79
element truss 394 14 91 1.0 79
element truss 395 32 55 1.0 82
element truss 396 87 68 1.0 82
element truss 397 70 65 1.0 82
element truss 398 63 13 1.0 82
element truss 399 65 66 1.0 82
element truss 400 55 24 1.0 82
element truss 401 13 29 1.0 82
element truss 402 44 48 1.0 82
element truss 403 68 44 1.0 82
element truss 404 29 20 1.0 82
element truss 405 66 43 1.0 82
element truss 406 43 69 1.0 82
element truss 407 48 38 1.0 82
element truss 408 24 21 1.0 82
element truss 409 24 44 1.0 85
element truss 410 13 65 1.0 85
element truss 411 13 43 1.0 85
element truss 412 20 43 1.0 85
element truss 413 24 38 1.0 85
element truss 414 124 126 1.0 76
element truss 415 97 115 1.0 76
element truss 416 100 10 1.0 76
element truss 417 125 128 1.0 76
element truss 418 118 10 1.0 76
element truss 419 97 99 1.0 76
element truss 420 118 18 1.0 76
element truss 421 125 111 1.0 76
element truss 422 114 126 1.0 76
element truss 423 92 115 1.0 76
element truss 424 123 67 1.0 79
element truss 425 120 65 1.0 85
element truss 426 89 14 1.0 79
element truss 427 113 132 1.0 70
element truss 428 64 133 1.0 70
element truss 429 131 97 1.0 70
element truss 430 88 55 1.0 70
element truss 431 106 131 1.0 82
element truss 432 121 63 1.0 70
element truss 433 89 65 1.0 72
element truss 434 87 67 1.0 72
element truss 435 117 84 1.0 85
element truss 436 6 100 1.0 70
element truss 437 90 68 1.0 70
element truss 438 70 71 1.0 70
element truss 439 102 129 1.0 70
element truss 440 129 85 1.0 70
element truss 441 98 90 1.0 70
element truss 442 85 70 1.0 70
element truss 443 126 102 1.0 70
element truss 444 68 86 1.0 70
element truss 445 128 57 1.0 70
element truss 446 102 34 1.0 70
element truss 447 57 98 1.0 70
element truss 448 103 98 1.0 70
element truss 449 119 65 1.0 72
element truss 450 87 72 1.0 72
element truss 451 28 23 1.0 72
element truss 452 112 127 1.0 72
element truss 453 112 82 1.0 72
element truss 454 28 116 1.0 72
element truss 455 114 116 1.0 72
element truss 456 8 96 1.0 72
element truss 457 56 131 1.0 70
element truss 458 133 131 1.0 70
element truss 459 40 31 1.0 70
element truss 460 31 42 1.0 70
element truss 461 21 30 1.0 70
element truss 462 41 47 1.0 70
element truss 463 30 41 1.0 70
element truss 464 132 59 1.0 70
element truss 465 65 91 1.0 72
element truss 466 65 46 1.0 72
element truss 467 132 6 1.0 70
element truss 468 60 15 1.0 85
element truss 469 131 134 1.0 70
element truss 470 59 100 1.0 70
element truss 471 55 30 1.0 70
element truss 472 29 62 1.0 70
element truss 473 121 29 1.0 70
element truss 474 51 55 1.0 70
element truss 475 44 49 1.0 72
element truss 476 91 43 1.0 72
element truss 477 46 43 1.0 72
element truss 478 44 25 1.0 72
element truss 479 46 28 1.0 72
element truss 480 113 12 1.0 82
element truss 481 55 64 1.0 70
element truss 482 25 38 1.0 72
element truss 483 25 82 1.0 72
element truss 484 43 52 1.0 72
element truss 485 43 23 1.0 72
element truss 486 42 118 1.0 70
element truss 487 47 92 1.0 70
element truss 488 72 44 1.0 72
element truss 489 72 33 1.0 72
element truss 490 96 46 1.0 72
element truss 491 112 93 1.0 85
element truss 492 8 124 1.0 72
element truss 493 124 60 1.0 72
element truss 494 117 125 1.0 72
element truss 495 125 112 1.0 72
element truss 496 67 44 1.0 72
element truss 497 84 112 1.0 85
element truss 498 128 103 1.0 70
element truss 499 86 67 1.0 76
element truss 500 96 60 1.0 72
element truss 501 117 33 1.0 72
element truss 502 100 110 1.0 76
element truss 503 134 99 1.0 76
element truss 504 89 71 1.0 76
element truss 505 106 117 1.0 85
element truss 506 85 66 1.0 70
element truss 507 61 68 1.0 70
element truss 508 66 71 1.0 70
element truss 509 111 57 1.0 70
element truss 510 68 54 1.0 70
element truss 511 126 101 1.0 70
element truss 512 67 54 1.0 76
element truss 513 61 48 1.0 70
element truss 514 27 66 1.0 70
element truss 515 57 109 1.0 70
element truss 516 109 61 1.0 70
element truss 517 34 27 1.0 70
element truss 518 101 34 1.0 70
element truss 519 130 101 1.0 70
element truss 520 14 121 1.0 76
element truss 521 101 95 1.0 70
element truss 522 111 135 1.0 70
element truss 523 48 54 1.0 70
element truss 524 66 50 1.0 70
element truss 525 27 69 1.0 70
element truss 526 48 53 1.0 70
element truss 527 94 48 1.0 70
element truss 528 135 109 1.0 70
element truss 529 54 49 1.0 76
element truss 530 91 50 1.0 76
element truss 531 88 45 1.0 76
element truss 532 109 94 1.0 70
element truss 533 69 50 1.0 70
element truss 534 95 27 1.0 70
element truss 535 123 88 1.0 76
element truss 536 122 14 1.0 76
element truss 537 71 91 1.0 76
element truss 538 34 85 1.0 70
element truss 539 98 61 1.0 70
element truss 540 37 29 1.0 70
element truss 541 29 40 1.0 70
element truss 542 51 21 1.0 70
element truss 543 47 97 1.0 70
element truss 544 127 111 1.0 76
element truss 545 114 130 1.0 76
element truss 546 12 46 1.0 85
element truss 547 58 25 1.0 85
element truss 548 16 23 1.0 85
element truss 549 58 72 1.0 85
element truss 550 22 25 1.0 85
element truss 551 16 46 1.0 85
element truss 552 141 32 1.0 82
element truss 553 110 124 1.0 79
element truss 554 99 108 1.0 79
element truss 555 120 63 1.0 82
element truss 556 64 58 1.0 82
element truss 557 119 85 1.0 82
element truss 558 62 12 1.0 82
element truss 559 72 61 1.0 82
element truss 560 72 90 1.0 82
element truss 561 46 85 1.0 82
element truss 562 62 16 1.0 82
element truss 563 30 58 1.0 82
element truss 564 46 27 1.0 82
element truss 565 23 27 1.0 82
element truss 566 25 94 1.0 82
element truss 567 25 61 1.0 82
element truss 568 40 16 1.0 82
element truss 569 30 22 1.0 82
element truss 570 12 119 1.0 85
element truss 571 64 105 1.0 82
element truss 572 105 72 1.0 85
element truss 573 32 87 1.0 85
element truss 574 107 83 1.0 85
element truss 575 133 83 1.0 82
element truss 576 9 96 1.0 85
element truss 577 9 132 1.0 82
element truss 578 108 117 1.0 72
element truss 579 122 63 1.0 70
element truss 580 106 83 1.0 72
element truss 581 9 12 1.0 72
element truss 582 12 120 1.0 72
element truss 583 83 105 1.0 72
element truss 584 105 32 1.0 72
element truss 585 32 123 1.0 72
element truss 586 120 14 1.0 72
element truss 587 99 84 1.0 72
element truss 588 84 83 1.0 72
element truss 589 32 45 1.0 72
element truss 590 58 32 1.0 72
element truss 591 83 58 1.0 72
element truss 592 26 58 1.0 72
element truss 593 84 26 1.0 72
element truss 594 115 84 1.0 72
element truss 595 115 93 1.0 72
element truss 596 58 24 1.0 72
element truss 597 24 45 1.0 72
element truss 598 26 22 1.0 72
element truss 599 93 26 1.0 72
element truss 600 22 24 1.0 72
element truss 601 24 39 1.0 72
element truss 602 60 114 1.0 72
element truss 603 33 112 1.0 72
element truss 604 33 25 1.0 72
element truss 605 60 28 1.0 72
element truss 606 108 128 1.0 76
element truss 607 88 141 1.0 70
element truss 608 141 64 1.0 70
element truss 609 63 113 1.0 70
element truss 610 64 56 1.0 70
element truss 611 124 104 1.0 76
element truss 612 63 62 1.0 70
element truss 613 62 132 1.0 70
element truss 614 104 102 1.0 70
