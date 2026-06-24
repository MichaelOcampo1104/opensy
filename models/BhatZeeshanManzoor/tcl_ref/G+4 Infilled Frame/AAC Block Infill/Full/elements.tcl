
# truss_elements truss
element truss 1 6 7 1.0 100
element truss 2 7 8 1.0 91


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 3), with Mesh Node = 9 (auxiliary for element 3)
node 252 12000 9200 4800
rigidLink beam 150 252

# Extra nodes for zeroLength
# node tag x y z
node 253 12000 9200 4800
node 254 12000 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 3 0.0 -0.0 1.0
element elasticBeamColumn 3 253 254 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 3

# zero_length_elements zeroLength
element zeroLength 913 252 253 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 914 254 6 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 4), with Mesh Node = 10 (auxiliary for element 4)
node 255 12000 14500 7900
rigidLink beam 10 255
# Geometric transformation command
geomTransf PDelta 4 -1.0 0.0 0.0
element forceBeamColumn 4 255 6 4 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 4), with Mesh Node = 10 (auxiliary for element 5)
node 256 12200 14500 8100
rigidLink beam 151 256


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 5), with Mesh Node = 11 (auxiliary for element 5)
node 257 15800 14500 8100
rigidLink beam 152 257

# Extra nodes for zeroLength
# node tag x y z
node 258 12200 14500 8100
node 259 15800 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 5 0.0 0.0 1.0
element elasticBeamColumn 5 258 259 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 5

# zero_length_elements zeroLength
element zeroLength 915 256 258 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 916 259 257 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 6), with Mesh Node = 12 (auxiliary for element 6)
node 260 16000 9200 8100
rigidLink beam 153 260


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 5), with Mesh Node = 11 (auxiliary for element 6)
node 261 16000 14300 8100
rigidLink beam 152 261

# Extra nodes for zeroLength
# node tag x y z
node 262 16000 9200 8100
node 263 16000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 6 0.0 -0.0 1.0
element elasticBeamColumn 6 262 263 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 6

# zero_length_elements zeroLength
element zeroLength 917 260 262 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 918 263 261 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 4), with Mesh Node = 10 (auxiliary for element 7)
node 264 12000 14500 8300
rigidLink beam 10 264


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 7), with Mesh Node = 13 (auxiliary for element 7)
node 265 12000 14500 11200
rigidLink beam 13 265
# Geometric transformation command
geomTransf PDelta 7 1.0 0.0 -0.0
element forceBeamColumn 7 264 265 7 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 6), with Mesh Node = 12 (auxiliary for element 8)
node 266 16000 9000 7900
rigidLink beam 12 266
# Geometric transformation command
geomTransf PDelta 8 1.0 0.0 -0.0
element forceBeamColumn 8 8 266 8 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 6), with Mesh Node = 12 (auxiliary for element 9)
node 267 16000 9000 8300
rigidLink beam 12 267


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 8), with Mesh Node = 14 (auxiliary for element 9)
node 268 16000 9000 11200
rigidLink beam 14 268
# Geometric transformation command
geomTransf PDelta 9 1.0 0.0 -0.0
element forceBeamColumn 9 267 268 9 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 8), with Mesh Node = 14 (auxiliary for element 10)
node 269 16000 9000 11600
rigidLink beam 14 269


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 9), with Mesh Node = 15 (auxiliary for element 10)
node 270 16000 9000 14500
rigidLink beam 15 270
# Geometric transformation command
geomTransf PDelta 10 1.0 0.0 -0.0
element forceBeamColumn 10 269 270 10 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 10), with Mesh Node = 16 (auxiliary for element 11)
node 271 8200 14500 8100
rigidLink beam 157 271


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 4), with Mesh Node = 10 (auxiliary for element 11)
node 272 11800 14500 8100
rigidLink beam 151 272

# Extra nodes for zeroLength
# node tag x y z
node 273 8200 14500 8100
node 274 11800 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 11 0.0 0.0 1.0
element elasticBeamColumn 11 273 274 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 11

# zero_length_elements zeroLength
element zeroLength 919 271 273 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 920 274 272 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 6), with Mesh Node = 12 (auxiliary for element 12)
node 275 16200 9000 8100
rigidLink beam 153 275


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 11), with Mesh Node = 17 (auxiliary for element 12)
node 276 19800 9000 8100
rigidLink beam 158 276

# Extra nodes for zeroLength
# node tag x y z
node 277 16200 9000 8100
node 278 19800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 12 0.0 0.0 1.0
element elasticBeamColumn 12 277 278 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 12

# zero_length_elements zeroLength
element zeroLength 921 275 277 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 922 278 276 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 12), with Mesh Node = 18 (auxiliary for element 13)
node 279 12200 9000 8100
rigidLink beam 159 279


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 6), with Mesh Node = 12 (auxiliary for element 13)
node 280 15800 9000 8100
rigidLink beam 153 280

# Extra nodes for zeroLength
# node tag x y z
node 281 12200 9000 8100
node 282 15800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 13 0.0 0.0 1.0
element elasticBeamColumn 13 281 282 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 13

# zero_length_elements zeroLength
element zeroLength 923 279 281 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 924 282 280 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 6), with Mesh Node = 12 (auxiliary for element 14)
node 283 16000 8800 8100
rigidLink beam 153 283

# Extra nodes for zeroLength
# node tag x y z
node 284 16000 5500 8100
node 285 16000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 14 0.0 -0.0 1.0
element elasticBeamColumn 14 284 285 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 14

# zero_length_elements zeroLength
element zeroLength 925 19 284 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 926 285 283 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 14), with Mesh Node = 20 (auxiliary for element 15)
node 286 20000 5700 8100
rigidLink beam 160 286


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 11), with Mesh Node = 17 (auxiliary for element 15)
node 287 20000 8800 8100
rigidLink beam 158 287

# Extra nodes for zeroLength
# node tag x y z
node 288 20000 5700 8100
node 289 20000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 15 0.0 -0.0 1.0
element elasticBeamColumn 15 288 289 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 15

# zero_length_elements zeroLength
element zeroLength 927 286 288 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 928 289 287 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 16)
node 290 20000 200 8100
rigidLink beam 161 290


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 14), with Mesh Node = 20 (auxiliary for element 16)
node 291 20000 5300 8100
rigidLink beam 160 291

# Extra nodes for zeroLength
# node tag x y z
node 292 20000 200 8100
node 293 20000 5300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 16 0.0 -0.0 1.0
element elasticBeamColumn 16 292 293 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 16

# zero_length_elements zeroLength
element zeroLength 929 290 292 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 930 293 291 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 17)
node 294 16000 200 8100
rigidLink beam 162 294

# Extra nodes for zeroLength
# node tag x y z
node 295 16000 200 8100
node 296 16000 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 17 0.0 -0.0 1.0
element elasticBeamColumn 17 295 296 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 17

# zero_length_elements zeroLength
element zeroLength 931 294 295 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 932 296 19 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 9), with Mesh Node = 15 (auxiliary for element 18)
node 297 16000 9000 14900
rigidLink beam 15 297
# Geometric transformation command
geomTransf PDelta 18 1.0 0.0 -0.0
element forceBeamColumn 18 297 23 18 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 11), with Mesh Node = 17 (auxiliary for element 19)
node 298 20000 9000 8300
rigidLink beam 17 298


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 19)
node 299 20000 9000 11200
rigidLink beam 24 299
# Geometric transformation command
geomTransf PDelta 19 1.0 0.0 -0.0
element forceBeamColumn 19 298 299 19 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 20)
node 300 20000 9000 5000
rigidLink beam 25 300


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 11), with Mesh Node = 17 (auxiliary for element 20)
node 301 20000 9000 7900
rigidLink beam 17 301
# Geometric transformation command
geomTransf PDelta 20 1.0 0.0 -0.0
element forceBeamColumn 20 300 301 20 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 21)
node 302 20000 9000 11600
rigidLink beam 24 302


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 21)
node 303 20000 9000 14500
rigidLink beam 26 303
# Geometric transformation command
geomTransf PDelta 21 1.0 0.0 -0.0
element forceBeamColumn 21 302 303 21 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 22)
node 304 20000 9200 11400
rigidLink beam 163 304


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 22)
node 305 20000 14300 11400
rigidLink beam 166 305

# Extra nodes for zeroLength
# node tag x y z
node 306 20000 9200 11400
node 307 20000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 22 0.0 -0.0 1.0
element elasticBeamColumn 22 306 307 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 22

# zero_length_elements zeroLength
element zeroLength 933 304 306 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 934 307 305 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 8), with Mesh Node = 14 (auxiliary for element 23)
node 308 16000 9200 11400
rigidLink beam 155 308


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 23)
node 309 16000 14300 11400
rigidLink beam 167 309

# Extra nodes for zeroLength
# node tag x y z
node 310 16000 9200 11400
node 311 16000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 23 0.0 -0.0 1.0
element elasticBeamColumn 23 310 311 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 23

# zero_length_elements zeroLength
element zeroLength 935 308 310 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 936 311 309 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 24)
node 312 20000 0 5000
rigidLink beam 29 312


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 24)
node 313 20000 0 7900
rigidLink beam 21 313
# Geometric transformation command
geomTransf PDelta 24 1.0 0.0 -0.0
element forceBeamColumn 24 312 313 24 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 25)
node 314 16200 14500 11400
rigidLink beam 167 314


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 25)
node 315 19800 14500 11400
rigidLink beam 166 315

# Extra nodes for zeroLength
# node tag x y z
node 316 16200 14500 11400
node 317 19800 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 25 0.0 0.0 1.0
element elasticBeamColumn 25 316 317 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 25

# zero_length_elements zeroLength
element zeroLength 937 314 316 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 938 317 315 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 8), with Mesh Node = 14 (auxiliary for element 26)
node 318 16200 9000 11400
rigidLink beam 155 318


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 26)
node 319 19800 9000 11400
rigidLink beam 163 319

# Extra nodes for zeroLength
# node tag x y z
node 320 16200 9000 11400
node 321 19800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 26 0.0 0.0 1.0
element elasticBeamColumn 26 320 321 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 26

# zero_length_elements zeroLength
element zeroLength 939 318 320 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 940 321 319 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 3), with Mesh Node = 9 (auxiliary for element 27)
node 322 12200 9000 4800
rigidLink beam 150 322

# Extra nodes for zeroLength
# node tag x y z
node 323 12200 9000 4800
node 324 16000 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 27 0.0 0.0 1.0
element elasticBeamColumn 27 323 324 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 27

# zero_length_elements zeroLength
element zeroLength 941 322 323 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 942 324 8 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 28)
node 325 16000 14300 4800
rigidLink beam 169 325

# Extra nodes for zeroLength
# node tag x y z
node 326 16000 9000 4800
node 327 16000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 28 0.0 -0.0 1.0
element elasticBeamColumn 28 326 327 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 28

# zero_length_elements zeroLength
element zeroLength 943 8 326 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 944 327 325 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 29)
node 328 8200 14500 4800
rigidLink beam 170 328

# Extra nodes for zeroLength
# node tag x y z
node 329 8200 14500 4800
node 330 12000 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 29 0.0 0.0 1.0
element elasticBeamColumn 29 329 330 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 29

# zero_length_elements zeroLength
element zeroLength 945 328 329 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 946 330 6 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 30)
node 331 20000 8800 4800
rigidLink beam 164 331

# Extra nodes for zeroLength
# node tag x y z
node 332 20000 5500 4800
node 333 20000 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 30 0.0 -0.0 1.0
element elasticBeamColumn 30 332 333 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 30

# zero_length_elements zeroLength
element zeroLength 947 32 332 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 948 333 331 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 31)
node 334 16000 5700 4800
rigidLink beam 171 334

# Extra nodes for zeroLength
# node tag x y z
node 335 16000 5700 4800
node 336 16000 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 31 0.0 -0.0 1.0
element elasticBeamColumn 31 335 336 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 31

# zero_length_elements zeroLength
element zeroLength 949 334 335 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 950 336 8 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 32)
node 337 15800 14500 4800
rigidLink beam 169 337

# Extra nodes for zeroLength
# node tag x y z
node 338 12000 14500 4800
node 339 15800 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 32 0.0 0.0 1.0
element elasticBeamColumn 32 338 339 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 32

# zero_length_elements zeroLength
element zeroLength 951 6 338 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 952 339 337 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 33)
node 340 19800 9000 4800
rigidLink beam 164 340

# Extra nodes for zeroLength
# node tag x y z
node 341 16000 9000 4800
node 342 19800 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 33 0.0 0.0 1.0
element elasticBeamColumn 33 341 342 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 33

# zero_length_elements zeroLength
element zeroLength 953 8 341 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 954 342 340 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 9), with Mesh Node = 15 (auxiliary for element 34)
node 343 16200 9000 14700
rigidLink beam 156 343


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 34)
node 344 19800 9000 14700
rigidLink beam 165 344

# Extra nodes for zeroLength
# node tag x y z
node 345 16200 9000 14700
node 346 19800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 34 0.0 0.0 1.0
element elasticBeamColumn 34 345 346 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 34

# zero_length_elements zeroLength
element zeroLength 955 343 345 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 956 346 344 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 35)
node 347 20000 9200 4800
rigidLink beam 164 347


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 35)
node 348 20000 14300 4800
rigidLink beam 172 348

# Extra nodes for zeroLength
# node tag x y z
node 349 20000 9200 4800
node 350 20000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 35 0.0 -0.0 1.0
element elasticBeamColumn 35 349 350 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 35

# zero_length_elements zeroLength
element zeroLength 957 347 349 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 958 350 348 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 29), with Mesh Node = 35 (auxiliary for element 36)
node 351 12200 9000 14700
rigidLink beam 173 351


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 9), with Mesh Node = 15 (auxiliary for element 36)
node 352 15800 9000 14700
rigidLink beam 156 352

# Extra nodes for zeroLength
# node tag x y z
node 353 12200 9000 14700
node 354 15800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 36 0.0 0.0 1.0
element elasticBeamColumn 36 353 354 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 36

# zero_length_elements zeroLength
element zeroLength 959 351 353 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 960 354 352 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 30), with Mesh Node = 36 (auxiliary for element 37)
node 355 8200 9000 14700
rigidLink beam 174 355


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 29), with Mesh Node = 35 (auxiliary for element 37)
node 356 11800 9000 14700
rigidLink beam 173 356

# Extra nodes for zeroLength
# node tag x y z
node 357 8200 9000 14700
node 358 11800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 37 0.0 0.0 1.0
element elasticBeamColumn 37 357 358 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 37

# zero_length_elements zeroLength
element zeroLength 961 355 357 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 962 358 356 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 38)
node 359 16000 14500 5000
rigidLink beam 30 359


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 5), with Mesh Node = 11 (auxiliary for element 38)
node 360 16000 14500 7900
rigidLink beam 11 360
# Geometric transformation command
geomTransf PDelta 38 1.0 0.0 -0.0
element forceBeamColumn 38 359 360 38 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 31), with Mesh Node = 37 (auxiliary for element 39)
node 361 19800 9000 18000
rigidLink beam 175 361

# Extra nodes for zeroLength
# node tag x y z
node 362 16000 9000 18000
node 363 19800 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 39 0.0 0.0 1.0
element elasticBeamColumn 39 362 363 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 39

# zero_length_elements zeroLength
element zeroLength 963 23 362 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 964 363 361 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 40)
node 364 12200 9000 18000
rigidLink beam 176 364

# Extra nodes for zeroLength
# node tag x y z
node 365 12200 9000 18000
node 366 16000 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 40 0.0 0.0 1.0
element elasticBeamColumn 40 365 366 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 40

# zero_length_elements zeroLength
element zeroLength 965 364 365 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 966 366 23 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 3), with Mesh Node = 9 (auxiliary for element 41)
node 367 12000 9000 4600
rigidLink beam 9 367
# Geometric transformation command
geomTransf PDelta 41 1.0 0.0 -0.0
element forceBeamColumn 41 7 367 41 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 42)
node 368 16000 5500 4600
rigidLink beam 33 368
# Geometric transformation command
geomTransf PDelta 42 1.0 0.0 -0.0
element forceBeamColumn 42 39 368 42 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 43 1.0 0.0 -0.0
element forceBeamColumn 43 40 6 43 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 44)
node 369 16000 14500 4600
rigidLink beam 30 369
# Geometric transformation command
geomTransf PDelta 44 1.0 0.0 -0.0
element forceBeamColumn 44 41 369 44 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 19), with Mesh Node = 25 (auxiliary for element 45)
node 370 20000 9000 4600
rigidLink beam 25 370
# Geometric transformation command
geomTransf PDelta 45 1.0 0.0 -0.0
element forceBeamColumn 45 42 370 45 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 46 1.0 0.0 -0.0
element forceBeamColumn 46 43 8 46 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 47)
node 371 8000 14500 4600
rigidLink beam 31 371
# Geometric transformation command
geomTransf PDelta 47 1.0 0.0 -0.0
element forceBeamColumn 47 44 371 47 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 48)
node 372 20000 14500 4600
rigidLink beam 34 372
# Geometric transformation command
geomTransf PDelta 48 1.0 0.0 -0.0
element forceBeamColumn 48 45 372 48 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 14), with Mesh Node = 20 (auxiliary for element 49)
node 373 20000 5500 8300
rigidLink beam 20 373
# Geometric transformation command
geomTransf PDelta 49 1.0 0.0 -0.0
element forceBeamColumn 49 373 46 49 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 50)
node 374 16000 5500 11200
rigidLink beam 47 374
# Geometric transformation command
geomTransf PDelta 50 1.0 0.0 -0.0
element forceBeamColumn 50 19 374 50 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 51)
node 375 20000 0 8300
rigidLink beam 21 375


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 51)
node 376 20000 0 11200
rigidLink beam 48 376
# Geometric transformation command
geomTransf PDelta 51 1.0 0.0 -0.0
element forceBeamColumn 51 375 376 51 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 52)
node 377 16000 5500 11600
rigidLink beam 47 377
# Geometric transformation command
geomTransf PDelta 52 1.0 0.0 -0.0
element forceBeamColumn 52 377 49 52 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 53)
node 378 20000 0 11600
rigidLink beam 48 378


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 44), with Mesh Node = 50 (auxiliary for element 53)
node 379 20000 0 14500
rigidLink beam 50 379
# Geometric transformation command
geomTransf PDelta 53 1.0 0.0 -0.0
element forceBeamColumn 53 378 379 53 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 44), with Mesh Node = 50 (auxiliary for element 54)
node 380 20000 0 14900
rigidLink beam 50 380


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 45), with Mesh Node = 51 (auxiliary for element 54)
node 381 20000 0 17800
rigidLink beam 51 381
# Geometric transformation command
geomTransf PDelta 54 1.0 0.0 -0.0
element forceBeamColumn 54 380 381 54 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 55)
node 382 20000 200 11400
rigidLink beam 178 382

# Extra nodes for zeroLength
# node tag x y z
node 383 20000 200 11400
node 384 20000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 55 0.0 -0.0 1.0
element elasticBeamColumn 55 383 384 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 55

# zero_length_elements zeroLength
element zeroLength 967 382 383 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 968 384 46 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 18), with Mesh Node = 24 (auxiliary for element 56)
node 385 20000 8800 11400
rigidLink beam 163 385

# Extra nodes for zeroLength
# node tag x y z
node 386 20000 5500 11400
node 387 20000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 56 0.0 -0.0 1.0
element elasticBeamColumn 56 386 387 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 56

# zero_length_elements zeroLength
element zeroLength 969 46 386 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 970 387 385 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 9), with Mesh Node = 15 (auxiliary for element 57)
node 388 16000 9200 14700
rigidLink beam 156 388


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 57)
node 389 16000 14300 14700
rigidLink beam 181 389

# Extra nodes for zeroLength
# node tag x y z
node 390 16000 9200 14700
node 391 16000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 57 0.0 -0.0 1.0
element elasticBeamColumn 57 390 391 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 57

# zero_length_elements zeroLength
element zeroLength 971 388 390 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 972 391 389 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 9), with Mesh Node = 15 (auxiliary for element 58)
node 392 16000 8800 14700
rigidLink beam 156 392

# Extra nodes for zeroLength
# node tag x y z
node 393 16000 5500 14700
node 394 16000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 58 0.0 -0.0 1.0
element elasticBeamColumn 58 393 394 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 58

# zero_length_elements zeroLength
element zeroLength 973 49 393 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 974 394 392 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 59)
node 395 20000 5700 14700
rigidLink beam 182 395


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 59)
node 396 20000 8800 14700
rigidLink beam 165 396

# Extra nodes for zeroLength
# node tag x y z
node 397 20000 5700 14700
node 398 20000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 59 0.0 -0.0 1.0
element elasticBeamColumn 59 397 398 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 59

# zero_length_elements zeroLength
element zeroLength 975 395 397 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 976 398 396 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 60)
node 399 20000 9200 14700
rigidLink beam 165 399


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 48), with Mesh Node = 54 (auxiliary for element 60)
node 400 20000 14300 14700
rigidLink beam 183 400

# Extra nodes for zeroLength
# node tag x y z
node 401 20000 9200 14700
node 402 20000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 60 0.0 -0.0 1.0
element elasticBeamColumn 60 401 402 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 60

# zero_length_elements zeroLength
element zeroLength 977 399 401 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 978 402 400 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 61)
node 403 12000 9200 18000
rigidLink beam 176 403


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 61)
node 404 12000 14300 18000
rigidLink beam 184 404

# Extra nodes for zeroLength
# node tag x y z
node 405 12000 9200 18000
node 406 12000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 61 0.0 -0.0 1.0
element elasticBeamColumn 61 405 406 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 61

# zero_length_elements zeroLength
element zeroLength 979 403 405 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 980 406 404 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 45), with Mesh Node = 51 (auxiliary for element 62)
node 407 20000 200 18000
rigidLink beam 180 407


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 62)
node 408 20000 5300 18000
rigidLink beam 185 408

# Extra nodes for zeroLength
# node tag x y z
node 409 20000 200 18000
node 410 20000 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 62 0.0 -0.0 1.0
element elasticBeamColumn 62 409 410 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 62

# zero_length_elements zeroLength
element zeroLength 981 407 409 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 982 410 408 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# truss_elements truss
element truss 63 19 8 1.0 85
element truss 64 35 57 1.0 85
element truss 65 58 9 1.0 85
element truss 66 18 59 1.0 85
element truss 67 57 18 1.0 85
element truss 68 23 52 1.0 82
element truss 69 60 15 1.0 82
element truss 70 61 57 1.0 82
element truss 71 38 62 1.0 82
element truss 72 63 10 1.0 82
element truss 73 55 35 1.0 82
element truss 74 35 13 1.0 82
element truss 75 62 63 1.0 82
element truss 76 13 18 1.0 82
element truss 77 64 47 1.0 82
element truss 78 65 58 1.0 82
element truss 79 58 66 1.0 82
element truss 80 57 67 1.0 82
element truss 81 67 59 1.0 82
element truss 82 10 9 1.0 82
element truss 83 18 6 1.0 82
element truss 84 52 14 1.0 82
element truss 85 15 28 1.0 82
element truss 86 47 22 1.0 82
element truss 87 14 11 1.0 82
element truss 88 68 19 1.0 82
element truss 89 49 68 1.0 82
element truss 90 22 33 1.0 82
element truss 91 19 69 1.0 82
element truss 92 28 12 1.0 82
element truss 93 11 8 1.0 82
element truss 94 12 30 1.0 82
element truss 95 38 15 1.0 72
element truss 96 70 35 1.0 72
element truss 97 38 36 1.0 72
element truss 98 56 49 1.0 72
element truss 99 49 14 1.0 85
element truss 100 53 71 1.0 72
element truss 101 65 22 1.0 70
element truss 102 67 68 1.0 70
element truss 103 72 65 1.0 70
element truss 104 68 21 1.0 70
element truss 105 73 67 1.0 70
element truss 106 46 26 1.0 79
element truss 107 46 17 1.0 79
element truss 108 20 25 1.0 79
element truss 109 20 24 1.0 79
element truss 110 32 17 1.0 79
element truss 111 53 24 1.0 79
element truss 112 26 27 1.0 76
element truss 113 48 20 1.0 76
element truss 114 50 46 1.0 76
element truss 115 24 54 1.0 76
element truss 116 21 46 1.0 76
element truss 117 48 53 1.0 76
element truss 118 21 32 1.0 76
element truss 119 24 74 1.0 76
element truss 120 17 27 1.0 76
element truss 121 29 20 1.0 76
element truss 122 75 61 1.0 70
element truss 123 64 48 1.0 70
element truss 124 71 64 1.0 82
element truss 125 15 47 1.0 85
element truss 126 76 50 1.0 70
element truss 127 52 55 1.0 70
element truss 128 55 77 1.0 70
element truss 129 62 78 1.0 70
element truss 130 77 79 1.0 70
element truss 131 27 52 1.0 70
element truss 132 54 28 1.0 70
element truss 133 52 13 1.0 70
element truss 134 28 62 1.0 70
element truss 135 60 62 1.0 70
element truss 136 70 80 1.0 72
element truss 137 81 36 1.0 72
element truss 138 18 82 1.0 72
element truss 139 12 25 1.0 72
element truss 140 12 9 1.0 72
element truss 141 18 8 1.0 72
element truss 142 17 8 1.0 72
element truss 143 23 35 1.0 72
element truss 144 65 64 1.0 70
element truss 145 83 64 1.0 70
element truss 146 84 67 1.0 70
element truss 147 67 69 1.0 70
element truss 148 85 72 1.0 70
element truss 149 66 22 1.0 70
element truss 150 72 66 1.0 70
element truss 151 61 68 1.0 70
element truss 152 80 86 1.0 72
element truss 153 80 87 1.0 72
element truss 154 61 76 1.0 70
element truss 155 14 19 1.0 85
element truss 156 64 51 1.0 70
element truss 157 68 50 1.0 70
element truss 158 88 72 1.0 70
element truss 159 89 73 1.0 70
element truss 160 90 89 1.0 70
element truss 161 91 88 1.0 70
element truss 162 86 92 1.0 72
element truss 163 87 92 1.0 72
element truss 164 87 18 1.0 72
element truss 165 75 93 1.0 82
element truss 166 88 94 1.0 70
element truss 167 95 9 1.0 72
element truss 168 92 96 1.0 72
element truss 169 92 82 1.0 72
element truss 170 69 21 1.0 70
element truss 171 22 29 1.0 70
element truss 172 36 97 1.0 72
element truss 173 36 63 1.0 72
element truss 174 35 87 1.0 72
element truss 175 12 33 1.0 85
element truss 176 23 26 1.0 72
element truss 177 26 14 1.0 72
element truss 178 15 24 1.0 72
element truss 179 24 12 1.0 72
element truss 180 98 97 1.0 72
element truss 181 47 12 1.0 85
element truss 182 54 60 1.0 70
element truss 183 99 98 1.0 76
element truss 184 35 14 1.0 72
element truss 185 15 63 1.0 72
element truss 186 50 56 1.0 76
element truss 187 51 53 1.0 76
element truss 188 71 15 1.0 85
element truss 189 77 100 1.0 70
element truss 190 100 101 1.0 70
element truss 191 74 28 1.0 70
element truss 192 27 11 1.0 70
element truss 193 98 102 1.0 76
element truss 194 16 100 1.0 70
element truss 195 28 10 1.0 70
element truss 196 10 103 1.0 70
element truss 197 13 16 1.0 70
element truss 198 11 13 1.0 70
element truss 199 34 11 1.0 70
element truss 200 104 90 1.0 76
element truss 201 11 6 1.0 70
element truss 202 74 30 1.0 70
element truss 203 105 102 1.0 70
element truss 204 100 106 1.0 70
element truss 205 16 107 1.0 70
element truss 206 105 108 1.0 70
element truss 207 31 105 1.0 70
element truss 208 30 10 1.0 70
element truss 209 102 109 1.0 76
element truss 210 86 106 1.0 76
element truss 211 10 31 1.0 70
element truss 212 107 106 1.0 70
element truss 213 6 16 1.0 70
element truss 214 110 104 1.0 76
element truss 215 101 86 1.0 76
element truss 216 13 77 1.0 70
element truss 217 62 103 1.0 70
element truss 218 111 89 1.0 70
element truss 219 89 84 1.0 70
element truss 220 91 85 1.0 70
element truss 221 22 48 1.0 70
element truss 222 25 74 1.0 76
element truss 223 17 34 1.0 76
element truss 224 93 87 1.0 85
element truss 225 112 95 1.0 85
element truss 226 113 82 1.0 85
element truss 227 112 36 1.0 85
element truss 228 114 95 1.0 85
element truss 229 113 87 1.0 85
element truss 230 56 26 1.0 79
element truss 231 53 37 1.0 79
element truss 232 94 112 1.0 82
element truss 233 70 77 1.0 82
element truss 234 73 93 1.0 82
element truss 235 36 103 1.0 82
element truss 236 36 78 1.0 82
element truss 237 87 77 1.0 82
element truss 238 73 113 1.0 82
element truss 239 72 112 1.0 82
element truss 240 87 16 1.0 82
element truss 241 82 16 1.0 82
element truss 242 95 31 1.0 82
element truss 243 95 103 1.0 82
element truss 244 84 113 1.0 82
element truss 245 72 114 1.0 82
element truss 246 93 70 1.0 85
element truss 247 94 115 1.0 82
element truss 248 115 36 1.0 85
element truss 249 116 81 1.0 85
element truss 250 38 117 1.0 85
element truss 251 83 117 1.0 82
element truss 252 118 35 1.0 85
element truss 253 118 61 1.0 82
element truss 254 37 15 1.0 72
element truss 255 110 119 1.0 70
element truss 256 71 117 1.0 72
element truss 257 118 93 1.0 72
element truss 258 93 120 1.0 72
element truss 259 117 115 1.0 72
element truss 260 115 116 1.0 72
element truss 261 116 121 1.0 72
element truss 262 120 104 1.0 72
element truss 263 53 47 1.0 72
element truss 264 47 117 1.0 72
element truss 265 116 122 1.0 72
element truss 266 112 116 1.0 72
element truss 267 117 112 1.0 72
element truss 268 58 112 1.0 72
element truss 269 47 58 1.0 72
element truss 270 20 47 1.0 72
element truss 271 20 33 1.0 72
element truss 272 112 123 1.0 72
element truss 273 123 122 1.0 72
element truss 274 58 114 1.0 72
element truss 275 33 58 1.0 72
element truss 276 114 123 1.0 72
element truss 277 123 124 1.0 72
element truss 278 14 17 1.0 72
element truss 279 63 12 1.0 72
element truss 280 63 95 1.0 72
element truss 281 14 18 1.0 72
element truss 282 37 54 1.0 76
element truss 283 125 94 1.0 70
element truss 284 119 75 1.0 70
element truss 285 94 65 1.0 70
element truss 286 26 126 1.0 76
element truss 287 119 73 1.0 70
element truss 288 73 61 1.0 70
element truss 289 126 52 1.0 70
element truss 290 127 108 1.0 87
element truss 291 32 39 1.0 91
element truss 292 7 82 1.0 91
element truss 293 9 43 1.0 91
element truss 294 85 128 1.0 100
element truss 295 8 42 1.0 91
element truss 296 82 129 1.0 91
element truss 297 130 127 1.0 100
element truss 298 130 128 1.0 103
element truss 299 131 129 1.0 103
element truss 300 114 132 1.0 103
element truss 301 31 132 1.0 100
element truss 302 130 132 1.0 91
element truss 303 25 43 1.0 91
element truss 304 114 133 1.0 100
element truss 305 131 134 1.0 100
element truss 306 9 132 1.0 91
element truss 307 82 44 1.0 100
element truss 308 130 135 1.0 91
element truss 309 107 136 1.0 87
element truss 310 31 127 1.0 87
element truss 311 34 41 1.0 87
element truss 312 44 107 1.0 87
element truss 313 6 44 1.0 87
element truss 314 41 6 1.0 87
element truss 315 40 31 1.0 87
element truss 316 30 40 1.0 87
element truss 317 29 137 1.0 95
element truss 318 138 111 1.0 95
element truss 319 124 139 1.0 95
element truss 320 108 135 1.0 95
element truss 321 135 124 1.0 98
element truss 322 96 138 1.0 98
element truss 323 9 140 1.0 103
element truss 324 69 39 1.0 100
element truss 325 39 8 1.0 103
element truss 326 33 43 1.0 103
element truss 327 33 141 1.0 100
element truss 328 30 43 1.0 100
element truss 329 8 41 1.0 100
element truss 330 9 40 1.0 100
element truss 331 59 142 1.0 100
element truss 332 59 7 1.0 103
element truss 333 66 140 1.0 100
element truss 334 66 141 1.0 87
element truss 335 69 142 1.0 87
element truss 336 84 142 1.0 87
element truss 337 84 134 1.0 87
element truss 338 66 133 1.0 87
element truss 339 85 139 1.0 87
element truss 340 128 124 1.0 91
element truss 341 140 114 1.0 91
element truss 342 143 131 1.0 91
element truss 343 39 59 1.0 91
element truss 344 33 140 1.0 91
element truss 345 114 128 1.0 91
element truss 346 59 143 1.0 91
element truss 347 131 138 1.0 91
element truss 348 111 134 1.0 87
element truss 349 137 33 1.0 91
element truss 350 82 143 1.0 103
element truss 351 69 144 1.0 87
element truss 352 29 141 1.0 87
element truss 353 85 133 1.0 87
element truss 354 137 25 1.0 98
element truss 355 84 143 1.0 100
element truss 356 42 34 1.0 95
element truss 357 32 42 1.0 98
element truss 358 144 32 1.0 95
element truss 359 25 45 1.0 95
element truss 360 107 129 1.0 100
element truss 361 96 136 1.0 95
element truss 362 96 129 1.0 91
element truss 363 45 30 1.0 87
element truss 364 76 49 1.0 82
element truss 365 49 23 1.0 85
element truss 366 49 118 1.0 72
element truss 367 49 46 1.0 72
element truss 368 49 57 1.0 72
element truss 369 57 93 1.0 72
element truss 370 93 145 1.0 72
element truss 371 145 104 1.0 72
element truss 372 46 19 1.0 72
element truss 373 57 113 1.0 72
element truss 374 19 57 1.0 72
element truss 375 145 146 1.0 72
element truss 376 113 145 1.0 72
element truss 377 32 19 1.0 72
element truss 378 19 59 1.0 72
element truss 379 113 131 1.0 72
element truss 380 59 113 1.0 72
element truss 381 131 146 1.0 72


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 382)
node 411 4000 200 4800
rigidLink beam 211 411

# Extra nodes for zeroLength
# node tag x y z
node 412 4000 200 4800
node 413 4000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 382 0.0 -0.0 1.0
element elasticBeamColumn 382 412 413 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 382

# zero_length_elements zeroLength
element zeroLength 983 411 412 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 984 413 131 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 383)
node 414 7800 5500 4800
rigidLink beam 237 414

# Extra nodes for zeroLength
# node tag x y z
node 415 4000 5500 4800
node 416 7800 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 383 0.0 0.0 1.0
element elasticBeamColumn 383 415 416 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 383

# zero_length_elements zeroLength
element zeroLength 985 131 415 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 986 416 414 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 384)
node 417 8000 5700 4800
rigidLink beam 237 417


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 384)
node 418 8000 8800 4800
rigidLink beam 208 418

# Extra nodes for zeroLength
# node tag x y z
node 419 8000 5700 4800
node 420 8000 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 384 0.0 -0.0 1.0
element elasticBeamColumn 384 419 420 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 384

# zero_length_elements zeroLength
element zeroLength 987 417 419 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 988 420 418 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 385)
node 421 8200 5500 4800
rigidLink beam 237 421

# Extra nodes for zeroLength
# node tag x y z
node 422 8200 5500 4800
node 423 12000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 385 0.0 0.0 1.0
element elasticBeamColumn 385 422 423 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 385

# zero_length_elements zeroLength
element zeroLength 989 421 422 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 990 423 59 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 386)
node 424 8000 5500 5000
rigidLink beam 114 424
# Geometric transformation command
geomTransf PDelta 386 1.0 0.0 -0.0
element forceBeamColumn 386 424 113 386 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 387)
node 425 4000 5500 7900
rigidLink beam 123 425
# Geometric transformation command
geomTransf PDelta 387 1.0 0.0 -0.0
element forceBeamColumn 387 131 425 387 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 388)
node 426 4000 5500 8300
rigidLink beam 123 426
# Geometric transformation command
geomTransf PDelta 388 1.0 0.0 -0.0
element forceBeamColumn 388 426 145 388 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 389)
node 427 8000 8800 8100
rigidLink beam 220 427

# Extra nodes for zeroLength
# node tag x y z
node 428 8000 5500 8100
node 429 8000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 389 0.0 -0.0 1.0
element elasticBeamColumn 389 428 429 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 389

# zero_length_elements zeroLength
element zeroLength 991 113 428 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 992 429 427 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 390)
node 430 4200 5500 8100
rigidLink beam 245 430

# Extra nodes for zeroLength
# node tag x y z
node 431 4200 5500 8100
node 432 8000 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 390 0.0 0.0 1.0
element elasticBeamColumn 390 431 432 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 390

# zero_length_elements zeroLength
element zeroLength 993 430 431 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 994 432 113 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 391)
node 433 11800 5500 8100
rigidLink beam 186 433

# Extra nodes for zeroLength
# node tag x y z
node 434 8000 5500 8100
node 435 11800 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 391 0.0 0.0 1.0
element elasticBeamColumn 391 434 435 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 391

# zero_length_elements zeroLength
element zeroLength 995 113 434 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 996 435 433 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 392)
node 436 8000 9200 8100
rigidLink beam 220 436


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 10), with Mesh Node = 16 (auxiliary for element 392)
node 437 8000 14300 8100
rigidLink beam 157 437

# Extra nodes for zeroLength
# node tag x y z
node 438 8000 9200 8100
node 439 8000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 392 0.0 -0.0 1.0
element elasticBeamColumn 392 438 439 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 392

# zero_length_elements zeroLength
element zeroLength 997 436 438 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 998 439 437 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 393)
node 440 12000 5700 8100
rigidLink beam 186 440


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 12), with Mesh Node = 18 (auxiliary for element 393)
node 441 12000 8800 8100
rigidLink beam 159 441

# Extra nodes for zeroLength
# node tag x y z
node 442 12000 5700 8100
node 443 12000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 393 0.0 -0.0 1.0
element elasticBeamColumn 393 442 443 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 393

# zero_length_elements zeroLength
element zeroLength 999 440 442 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1000 443 441 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 394)
node 444 4000 200 8100
rigidLink beam 215 444


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 394)
node 445 4000 5300 8100
rigidLink beam 245 445

# Extra nodes for zeroLength
# node tag x y z
node 446 4000 200 8100
node 447 4000 5300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 394 0.0 -0.0 1.0
element elasticBeamColumn 394 446 447 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 394

# zero_length_elements zeroLength
element zeroLength 1001 444 446 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1002 447 445 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 395)
node 448 8000 200 8100
rigidLink beam 199 448

# Extra nodes for zeroLength
# node tag x y z
node 449 8000 200 8100
node 450 8000 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 395 0.0 -0.0 1.0
element elasticBeamColumn 395 449 450 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 395

# zero_length_elements zeroLength
element zeroLength 1003 448 449 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1004 450 113 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 396)
node 451 12000 200 8100
rigidLink beam 194 451


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 396)
node 452 12000 5300 8100
rigidLink beam 186 452

# Extra nodes for zeroLength
# node tag x y z
node 453 12000 200 8100
node 454 12000 5300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 396 0.0 -0.0 1.0
element elasticBeamColumn 396 453 454 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 396

# zero_length_elements zeroLength
element zeroLength 1005 451 453 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1006 454 452 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 397)
node 455 4000 5500 14500
rigidLink beam 116 455
# Geometric transformation command
geomTransf PDelta 397 1.0 0.0 -0.0
element forceBeamColumn 397 145 455 397 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 12), with Mesh Node = 18 (auxiliary for element 398)
node 456 12000 9000 8300
rigidLink beam 18 456


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 398)
node 457 12000 9000 11200
rigidLink beam 63 457
# Geometric transformation command
geomTransf PDelta 398 1.0 0.0 -0.0
element forceBeamColumn 398 456 457 398 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 399)
node 458 12000 9200 11400
rigidLink beam 190 458


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 7), with Mesh Node = 13 (auxiliary for element 399)
node 459 12000 14300 11400
rigidLink beam 154 459

# Extra nodes for zeroLength
# node tag x y z
node 460 12000 9200 11400
node 461 12000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 399 0.0 -0.0 1.0
element elasticBeamColumn 399 460 461 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 399

# zero_length_elements zeroLength
element zeroLength 1007 458 460 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1008 461 459 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 400)
node 462 8000 9000 4600
rigidLink beam 82 462
# Geometric transformation command
geomTransf PDelta 400 1.0 0.0 -0.0
element forceBeamColumn 400 132 462 400 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 401)
node 463 4000 0 4600
rigidLink beam 85 463
# Geometric transformation command
geomTransf PDelta 401 1.0 0.0 -0.0
element forceBeamColumn 401 134 463 401 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 105), with Mesh Node = 111 (auxiliary for element 402)
node 464 200 0 4800
rigidLink beam 235 464


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 402)
node 465 3800 0 4800
rigidLink beam 211 465

# Extra nodes for zeroLength
# node tag x y z
node 466 200 0 4800
node 467 3800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 402 0.0 0.0 1.0
element elasticBeamColumn 402 466 467 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 402

# zero_length_elements zeroLength
element zeroLength 1009 464 466 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1010 467 465 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# Extra nodes for zeroLength
# node tag x y z
node 468 4000 5500 4800
node 469 4000 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 403 0.0 -0.0 1.0
element elasticBeamColumn 403 468 469 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 403

# zero_length_elements zeroLength
element zeroLength 1011 131 468 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1012 469 130 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 105), with Mesh Node = 111 (auxiliary for element 404)
node 470 0 200 4800
rigidLink beam 235 470


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 404)
node 471 0 5300 4800
rigidLink beam 246 471

# Extra nodes for zeroLength
# node tag x y z
node 472 0 200 4800
node 473 0 5300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 404 0.0 -0.0 1.0
element elasticBeamColumn 404 472 473 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 404

# zero_length_elements zeroLength
element zeroLength 1013 470 472 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1014 473 471 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 405)
node 474 4200 0 4800
rigidLink beam 211 474


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 405)
node 475 7800 0 4800
rigidLink beam 210 475

# Extra nodes for zeroLength
# node tag x y z
node 476 4200 0 4800
node 477 7800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 405 0.0 0.0 1.0
element elasticBeamColumn 405 476 477 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 405

# zero_length_elements zeroLength
element zeroLength 1015 474 476 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1016 477 475 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 406)
node 478 8200 0 4800
rigidLink beam 210 478


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 406)
node 479 11800 0 4800
rigidLink beam 193 479

# Extra nodes for zeroLength
# node tag x y z
node 480 8200 0 4800
node 481 11800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 406 0.0 0.0 1.0
element elasticBeamColumn 406 480 481 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 406

# zero_length_elements zeroLength
element zeroLength 1017 478 480 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1018 481 479 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 407)
node 482 200 5500 4800
rigidLink beam 246 482

# Extra nodes for zeroLength
# node tag x y z
node 483 200 5500 4800
node 484 4000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 407 0.0 0.0 1.0
element elasticBeamColumn 407 483 484 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 407

# zero_length_elements zeroLength
element zeroLength 1019 482 483 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1020 484 131 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 408)
node 485 12200 0 4800
rigidLink beam 193 485


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 408)
node 486 15800 0 4800
rigidLink beam 196 486

# Extra nodes for zeroLength
# node tag x y z
node 487 12200 0 4800
node 488 15800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 408 0.0 0.0 1.0
element elasticBeamColumn 408 487 488 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 408

# zero_length_elements zeroLength
element zeroLength 1021 485 487 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1022 488 486 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 409)
node 489 4000 9000 7900
rigidLink beam 92 489
# Geometric transformation command
geomTransf PDelta 409 1.0 0.0 -0.0
element forceBeamColumn 409 130 489 409 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 410)
node 490 4000 9000 8300
rigidLink beam 92 490


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 410)
node 491 4000 9000 11200
rigidLink beam 97 491
# Geometric transformation command
geomTransf PDelta 410 1.0 0.0 -0.0
element forceBeamColumn 410 490 491 410 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 116), with Mesh Node = 122 (auxiliary for element 411)
node 492 200 5500 11400
rigidLink beam 244 492

# Extra nodes for zeroLength
# node tag x y z
node 493 200 5500 11400
node 494 4000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 411 0.0 0.0 1.0
element elasticBeamColumn 411 493 494 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 411

# zero_length_elements zeroLength
element zeroLength 1023 492 493 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1024 494 145 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 412)
node 495 7800 9000 4800
rigidLink beam 208 495

# Extra nodes for zeroLength
# node tag x y z
node 496 4000 9000 4800
node 497 7800 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 412 0.0 0.0 1.0
element elasticBeamColumn 412 496 497 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 412

# zero_length_elements zeroLength
element zeroLength 1025 130 496 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1026 497 495 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 413)
node 498 4200 9000 11400
rigidLink beam 222 498


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 413)
node 499 7800 9000 11400
rigidLink beam 213 499

# Extra nodes for zeroLength
# node tag x y z
node 500 4200 9000 11400
node 501 7800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 413 0.0 0.0 1.0
element elasticBeamColumn 413 500 501 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 413

# zero_length_elements zeroLength
element zeroLength 1027 498 500 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1028 501 499 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 414)
node 502 4000 8800 11400
rigidLink beam 222 502

# Extra nodes for zeroLength
# node tag x y z
node 503 4000 5500 11400
node 504 4000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 414 0.0 -0.0 1.0
element elasticBeamColumn 414 503 504 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 414

# zero_length_elements zeroLength
element zeroLength 1029 145 503 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1030 504 502 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 415)
node 505 12000 0 5000
rigidLink beam 66 505


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 415)
node 506 12000 0 7900
rigidLink beam 67 506
# Geometric transformation command
geomTransf PDelta 415 1.0 0.0 -0.0
element forceBeamColumn 415 505 506 415 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 416)
node 507 16000 0 5000
rigidLink beam 69 507


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 416)
node 508 16000 0 7900
rigidLink beam 22 508
# Geometric transformation command
geomTransf PDelta 416 1.0 0.0 -0.0
element forceBeamColumn 416 507 508 416 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 417)
node 509 4200 14500 8100
rigidLink beam 229 509


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 10), with Mesh Node = 16 (auxiliary for element 417)
node 510 7800 14500 8100
rigidLink beam 157 510

# Extra nodes for zeroLength
# node tag x y z
node 511 4200 14500 8100
node 512 7800 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 417 0.0 0.0 1.0
element elasticBeamColumn 417 511 512 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 417

# zero_length_elements zeroLength
element zeroLength 1031 509 511 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1032 512 510 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 418)
node 513 4000 9200 8100
rigidLink beam 218 513


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 418)
node 514 4000 14300 8100
rigidLink beam 229 514

# Extra nodes for zeroLength
# node tag x y z
node 515 4000 9200 8100
node 516 4000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 418 0.0 -0.0 1.0
element elasticBeamColumn 418 515 516 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 418

# zero_length_elements zeroLength
element zeroLength 1033 513 515 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1034 516 514 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 419)
node 517 4200 9000 8100
rigidLink beam 218 517


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 419)
node 518 7800 9000 8100
rigidLink beam 220 518

# Extra nodes for zeroLength
# node tag x y z
node 519 4200 9000 8100
node 520 7800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 419 0.0 0.0 1.0
element elasticBeamColumn 419 519 520 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 419

# zero_length_elements zeroLength
element zeroLength 1035 517 519 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1036 520 518 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 420)
node 521 200 9000 8100
rigidLink beam 233 521


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 420)
node 522 3800 9000 8100
rigidLink beam 218 522

# Extra nodes for zeroLength
# node tag x y z
node 523 200 9000 8100
node 524 3800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 420 0.0 0.0 1.0
element elasticBeamColumn 420 523 524 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 420

# zero_length_elements zeroLength
element zeroLength 1037 521 523 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1038 524 522 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 421)
node 525 3800 14500 8100
rigidLink beam 229 525


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 421)
node 526 200 14500 8100
rigidLink beam 230 526

# Extra nodes for zeroLength
# node tag x y z
node 527 3800 14500 8100
node 528 200 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 421 0.0 0.0 1.0
element elasticBeamColumn 421 527 528 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 421

# zero_length_elements zeroLength
element zeroLength 1039 525 527 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1040 528 526 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 422)
node 529 200 0 8100
rigidLink beam 217 529


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 422)
node 530 3800 0 8100
rigidLink beam 215 530

# Extra nodes for zeroLength
# node tag x y z
node 531 200 0 8100
node 532 3800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 422 0.0 0.0 1.0
element elasticBeamColumn 422 531 532 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 422

# zero_length_elements zeroLength
element zeroLength 1041 529 531 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1042 532 530 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 423)
node 533 0 9000 5000
rigidLink beam 96 533


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 423)
node 534 0 9000 7900
rigidLink beam 109 534
# Geometric transformation command
geomTransf PDelta 423 1.0 0.0 -0.0
element forceBeamColumn 423 533 534 423 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 424)
node 535 3800 5500 8100
rigidLink beam 245 535

# Extra nodes for zeroLength
# node tag x y z
node 536 0 5500 8100
node 537 3800 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 424 0.0 0.0 1.0
element elasticBeamColumn 424 536 537 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 424

# zero_length_elements zeroLength
element zeroLength 1043 146 536 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1044 537 535 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 425)
node 538 0 9200 8100
rigidLink beam 233 538


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 425)
node 539 0 14300 8100
rigidLink beam 230 539

# Extra nodes for zeroLength
# node tag x y z
node 540 0 9200 8100
node 541 0 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 425 0.0 -0.0 1.0
element elasticBeamColumn 425 540 541 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 425

# zero_length_elements zeroLength
element zeroLength 1045 538 540 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1046 541 539 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 117), with Mesh Node = 123 (auxiliary for element 426)
node 542 4000 5700 8100
rigidLink beam 245 542


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 86), with Mesh Node = 92 (auxiliary for element 426)
node 543 4000 8800 8100
rigidLink beam 218 543

# Extra nodes for zeroLength
# node tag x y z
node 544 4000 5700 8100
node 545 4000 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 426 0.0 -0.0 1.0
element elasticBeamColumn 426 544 545 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 426

# zero_length_elements zeroLength
element zeroLength 1047 542 544 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1048 545 543 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 102), with Mesh Node = 108 (auxiliary for element 427)
node 546 0 14500 5000
rigidLink beam 108 546


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 427)
node 547 0 14500 7900
rigidLink beam 106 547
# Geometric transformation command
geomTransf PDelta 427 1.0 0.0 -0.0
element forceBeamColumn 427 546 547 427 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 100), with Mesh Node = 106 (auxiliary for element 428)
node 548 0 14500 8300
rigidLink beam 106 548


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 428)
node 549 0 14500 11200
rigidLink beam 102 549
# Geometric transformation command
geomTransf PDelta 428 1.0 0.0 -0.0
element forceBeamColumn 428 548 549 428 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 429)
node 550 4000 0 8300
rigidLink beam 89 550


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 429)
node 551 4000 0 11200
rigidLink beam 88 551
# Geometric transformation command
geomTransf PDelta 429 1.0 0.0 -0.0
element forceBeamColumn 429 550 551 429 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 79), with Mesh Node = 85 (auxiliary for element 430)
node 552 4000 0 5000
rigidLink beam 85 552


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 430)
node 553 4000 0 7900
rigidLink beam 89 553
# Geometric transformation command
geomTransf PDelta 430 1.0 0.0 -0.0
element forceBeamColumn 430 552 553 430 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 431)
node 554 8000 0 5000
rigidLink beam 84 554


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 431)
node 555 8000 0 7900
rigidLink beam 72 555
# Geometric transformation command
geomTransf PDelta 431 1.0 0.0 -0.0
element forceBeamColumn 431 554 555 431 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 432)
node 556 12000 0 8300
rigidLink beam 67 556


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 432)
node 557 12000 0 11200
rigidLink beam 65 557
# Geometric transformation command
geomTransf PDelta 432 1.0 0.0 -0.0
element forceBeamColumn 432 556 557 432 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 7), with Mesh Node = 13 (auxiliary for element 433)
node 558 12200 14500 11400
rigidLink beam 154 558


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 433)
node 559 15800 14500 11400
rigidLink beam 167 559

# Extra nodes for zeroLength
# node tag x y z
node 560 12200 14500 11400
node 561 15800 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 433 0.0 0.0 1.0
element elasticBeamColumn 433 560 561 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 433

# zero_length_elements zeroLength
element zeroLength 1049 558 560 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1050 561 559 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 434)
node 562 8000 5700 11400
rigidLink beam 236 562


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 434)
node 563 8000 8800 11400
rigidLink beam 213 563

# Extra nodes for zeroLength
# node tag x y z
node 564 8000 5700 11400
node 565 8000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 434 0.0 -0.0 1.0
element elasticBeamColumn 434 564 565 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 434

# zero_length_elements zeroLength
element zeroLength 1051 562 564 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1052 565 563 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 435)
node 566 16000 0 8300
rigidLink beam 22 566


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 435)
node 567 16000 0 11200
rigidLink beam 68 567
# Geometric transformation command
geomTransf PDelta 435 1.0 0.0 -0.0
element forceBeamColumn 435 566 567 435 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 436)
node 568 12200 9000 11400
rigidLink beam 190 568


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 8), with Mesh Node = 14 (auxiliary for element 436)
node 569 15800 9000 11400
rigidLink beam 155 569

# Extra nodes for zeroLength
# node tag x y z
node 570 12200 9000 11400
node 571 15800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 436 0.0 0.0 1.0
element elasticBeamColumn 436 570 571 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 436

# zero_length_elements zeroLength
element zeroLength 1053 568 570 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1054 571 569 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 437)
node 572 7800 5500 11400
rigidLink beam 236 572

# Extra nodes for zeroLength
# node tag x y z
node 573 4000 5500 11400
node 574 7800 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 437 0.0 0.0 1.0
element elasticBeamColumn 437 573 574 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 437

# zero_length_elements zeroLength
element zeroLength 1055 145 573 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1056 574 572 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 438)
node 575 8200 9000 11400
rigidLink beam 213 575


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 438)
node 576 11800 9000 11400
rigidLink beam 190 576

# Extra nodes for zeroLength
# node tag x y z
node 577 8200 9000 11400
node 578 11800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 438 0.0 0.0 1.0
element elasticBeamColumn 438 577 578 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 438

# zero_length_elements zeroLength
element zeroLength 1057 575 577 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1058 578 576 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 439)
node 579 8000 9200 11400
rigidLink beam 213 579


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 439)
node 580 8000 14300 11400
rigidLink beam 228 580

# Extra nodes for zeroLength
# node tag x y z
node 581 8000 9200 11400
node 582 8000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 439 0.0 -0.0 1.0
element elasticBeamColumn 439 581 582 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 439

# zero_length_elements zeroLength
element zeroLength 1059 579 581 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1060 582 580 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 440)
node 583 4200 0 11400
rigidLink beam 214 583


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 67), with Mesh Node = 73 (auxiliary for element 440)
node 584 7800 0 11400
rigidLink beam 200 584

# Extra nodes for zeroLength
# node tag x y z
node 585 4200 0 11400
node 586 7800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 440 0.0 0.0 1.0
element elasticBeamColumn 440 585 586 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 440

# zero_length_elements zeroLength
element zeroLength 1061 583 585 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1062 586 584 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 441)
node 587 4000 200 11400
rigidLink beam 214 587

# Extra nodes for zeroLength
# node tag x y z
node 588 4000 200 11400
node 589 4000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 441 0.0 -0.0 1.0
element elasticBeamColumn 441 588 589 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 441

# zero_length_elements zeroLength
element zeroLength 1063 587 588 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1064 589 145 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 442)
node 590 4200 5500 14700
rigidLink beam 239 590

# Extra nodes for zeroLength
# node tag x y z
node 591 4200 5500 14700
node 592 8000 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 442 0.0 0.0 1.0
element elasticBeamColumn 442 591 592 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 442

# zero_length_elements zeroLength
element zeroLength 1065 590 591 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1066 592 93 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 443)
node 593 4000 200 14700
rigidLink beam 241 593


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 443)
node 594 4000 5300 14700
rigidLink beam 239 594

# Extra nodes for zeroLength
# node tag x y z
node 595 4000 200 14700
node 596 4000 5300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 443 0.0 -0.0 1.0
element elasticBeamColumn 443 595 596 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 443

# zero_length_elements zeroLength
element zeroLength 1067 593 595 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1068 596 594 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 444)
node 597 4200 0 14700
rigidLink beam 241 597


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 444)
node 598 7800 0 14700
rigidLink beam 219 598

# Extra nodes for zeroLength
# node tag x y z
node 599 4200 0 14700
node 600 7800 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 444 0.0 0.0 1.0
element elasticBeamColumn 444 599 600 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 444

# zero_length_elements zeroLength
element zeroLength 1069 597 599 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1070 600 598 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 445)
node 601 4000 9000 11600
rigidLink beam 97 601


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 74), with Mesh Node = 80 (auxiliary for element 445)
node 602 4000 9000 14500
rigidLink beam 80 602
# Geometric transformation command
geomTransf PDelta 445 1.0 0.0 -0.0
element forceBeamColumn 445 601 602 445 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 446)
node 603 4000 14500 8300
rigidLink beam 105 603


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 446)
node 604 4000 14500 11200
rigidLink beam 100 604
# Geometric transformation command
geomTransf PDelta 446 1.0 0.0 -0.0
element forceBeamColumn 446 603 604 446 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 447)
node 605 200 9000 14700
rigidLink beam 223 605


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 74), with Mesh Node = 80 (auxiliary for element 447)
node 606 3800 9000 14700
rigidLink beam 206 606

# Extra nodes for zeroLength
# node tag x y z
node 607 200 9000 14700
node 608 3800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 447 0.0 0.0 1.0
element elasticBeamColumn 447 607 608 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 447

# zero_length_elements zeroLength
element zeroLength 1071 605 607 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1072 608 606 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 74), with Mesh Node = 80 (auxiliary for element 448)
node 609 4000 9200 14700
rigidLink beam 206 609


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 141), with Mesh Node = 147 (auxiliary for element 448)
node 610 4000 14300 14700
rigidLink beam 249 610

# Extra nodes for zeroLength
# node tag x y z
node 611 4000 9200 14700
node 612 4000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 448 0.0 -0.0 1.0
element elasticBeamColumn 448 611 612 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 448

# zero_length_elements zeroLength
element zeroLength 1073 609 611 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1074 612 610 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 449)
node 613 4000 14500 11600
rigidLink beam 100 613


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 141), with Mesh Node = 147 (auxiliary for element 449)
node 614 4000 14500 14500
rigidLink beam 147 614
# Geometric transformation command
geomTransf PDelta 449 1.0 0.0 -0.0
element forceBeamColumn 449 613 614 449 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 450)
node 615 4000 14500 5000
rigidLink beam 107 615


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 99), with Mesh Node = 105 (auxiliary for element 450)
node 616 4000 14500 7900
rigidLink beam 105 616
# Geometric transformation command
geomTransf PDelta 450 1.0 0.0 -0.0
element forceBeamColumn 450 615 616 450 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 141), with Mesh Node = 147 (auxiliary for element 451)
node 617 4000 14500 14900
rigidLink beam 147 617


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 73), with Mesh Node = 79 (auxiliary for element 451)
node 618 4000 14500 17800
rigidLink beam 79 618
# Geometric transformation command
geomTransf PDelta 451 1.0 0.0 -0.0
element forceBeamColumn 451 617 618 451 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 452)
node 619 0 8800 14700
rigidLink beam 223 619

# Extra nodes for zeroLength
# node tag x y z
node 620 0 5500 14700
node 621 0 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 452 0.0 -0.0 1.0
element elasticBeamColumn 452 620 621 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 452

# zero_length_elements zeroLength
element zeroLength 1075 104 620 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1076 621 619 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 453)
node 622 0 9200 14700
rigidLink beam 223 622


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 453)
node 623 0 14300 14700
rigidLink beam 226 623

# Extra nodes for zeroLength
# node tag x y z
node 624 0 9200 14700
node 625 0 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 453 0.0 -0.0 1.0
element elasticBeamColumn 453 624 625 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 453

# zero_length_elements zeroLength
element zeroLength 1077 622 624 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1078 625 623 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 74), with Mesh Node = 80 (auxiliary for element 454)
node 626 4200 9000 14700
rigidLink beam 206 626


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 30), with Mesh Node = 36 (auxiliary for element 454)
node 627 7800 9000 14700
rigidLink beam 174 627

# Extra nodes for zeroLength
# node tag x y z
node 628 4200 9000 14700
node 629 7800 9000 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 454 0.0 0.0 1.0
element elasticBeamColumn 454 628 629 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 454

# zero_length_elements zeroLength
element zeroLength 1079 626 628 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1080 629 627 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 102), with Mesh Node = 108 (auxiliary for element 455)
node 630 0 14500 4600
rigidLink beam 108 630
# Geometric transformation command
geomTransf PDelta 455 1.0 0.0 -0.0
element forceBeamColumn 455 136 630 455 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 456)
node 631 0 5500 4600
rigidLink beam 124 631
# Geometric transformation command
geomTransf PDelta 456 1.0 0.0 -0.0
element forceBeamColumn 456 138 631 456 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 457)
node 632 0 9000 4600
rigidLink beam 96 632
# Geometric transformation command
geomTransf PDelta 457 1.0 0.0 -0.0
element forceBeamColumn 457 135 632 457 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 458 1.0 0.0 -0.0
element forceBeamColumn 458 129 130 458 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 105), with Mesh Node = 111 (auxiliary for element 459)
node 633 0 0 4600
rigidLink beam 111 633
# Geometric transformation command
geomTransf PDelta 459 1.0 0.0 -0.0
element forceBeamColumn 459 139 633 459 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 460)
node 634 4000 14500 4600
rigidLink beam 107 634
# Geometric transformation command
geomTransf PDelta 460 1.0 0.0 -0.0
element forceBeamColumn 460 127 634 460 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 461)
node 635 8000 5500 4600
rigidLink beam 114 635
# Geometric transformation command
geomTransf PDelta 461 1.0 0.0 -0.0
element forceBeamColumn 461 143 635 461 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 462 1.0 0.0 -0.0
element forceBeamColumn 462 128 131 462 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 463 1.0 0.0 -0.0
element forceBeamColumn 463 140 59 463 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 464)
node 636 8000 5500 11200
rigidLink beam 112 636
# Geometric transformation command
geomTransf PDelta 464 1.0 0.0 -0.0
element forceBeamColumn 464 113 636 464 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 465)
node 637 8000 0 8300
rigidLink beam 72 637


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 67), with Mesh Node = 73 (auxiliary for element 465)
node 638 8000 0 11200
rigidLink beam 73 638
# Geometric transformation command
geomTransf PDelta 465 1.0 0.0 -0.0
element forceBeamColumn 465 637 638 465 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 3), with Mesh Node = 9 (auxiliary for element 466)
node 639 12000 9000 5000
rigidLink beam 9 639


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 12), with Mesh Node = 18 (auxiliary for element 466)
node 640 12000 9000 7900
rigidLink beam 18 640
# Geometric transformation command
geomTransf PDelta 466 1.0 0.0 -0.0
element forceBeamColumn 466 639 640 466 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 467)
node 641 12000 5500 8300
rigidLink beam 58 641
# Geometric transformation command
geomTransf PDelta 467 1.0 0.0 -0.0
element forceBeamColumn 467 641 57 467 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 468)
node 642 12000 5500 14500
rigidLink beam 117 642
# Geometric transformation command
geomTransf PDelta 468 1.0 0.0 -0.0
element forceBeamColumn 468 57 642 468 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 469)
node 643 12000 5500 14900
rigidLink beam 117 643
# Geometric transformation command
geomTransf PDelta 469 1.0 0.0 -0.0
element forceBeamColumn 469 643 118 469 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 470)
node 644 8200 5500 11400
rigidLink beam 236 644

# Extra nodes for zeroLength
# node tag x y z
node 645 8200 5500 11400
node 646 12000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 470 0.0 0.0 1.0
element elasticBeamColumn 470 645 646 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 470

# zero_length_elements zeroLength
element zeroLength 1081 644 645 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1082 646 57 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 471)
node 647 12000 8800 11400
rigidLink beam 190 647

# Extra nodes for zeroLength
# node tag x y z
node 648 12000 5500 11400
node 649 12000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 471 0.0 -0.0 1.0
element elasticBeamColumn 471 648 649 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 471

# zero_length_elements zeroLength
element zeroLength 1083 57 648 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1084 649 647 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 472)
node 650 15800 5500 11400
rigidLink beam 177 650

# Extra nodes for zeroLength
# node tag x y z
node 651 12000 5500 11400
node 652 15800 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 472 0.0 0.0 1.0
element elasticBeamColumn 472 651 652 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 472

# zero_length_elements zeroLength
element zeroLength 1085 57 651 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1086 652 650 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 473)
node 653 16000 5700 11400
rigidLink beam 177 653


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 8), with Mesh Node = 14 (auxiliary for element 473)
node 654 16000 8800 11400
rigidLink beam 155 654

# Extra nodes for zeroLength
# node tag x y z
node 655 16000 5700 11400
node 656 16000 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 473 0.0 -0.0 1.0
element elasticBeamColumn 473 655 656 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 473

# zero_length_elements zeroLength
element zeroLength 1087 653 655 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1088 656 654 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 474)
node 657 16200 5500 11400
rigidLink beam 177 657

# Extra nodes for zeroLength
# node tag x y z
node 658 16200 5500 11400
node 659 20000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 474 0.0 0.0 1.0
element elasticBeamColumn 474 658 659 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 474

# zero_length_elements zeroLength
element zeroLength 1089 657 658 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1090 659 46 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 67), with Mesh Node = 73 (auxiliary for element 475)
node 660 8200 0 11400
rigidLink beam 200 660


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 475)
node 661 11800 0 11400
rigidLink beam 192 661

# Extra nodes for zeroLength
# node tag x y z
node 662 8200 0 11400
node 663 11800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 475 0.0 0.0 1.0
element elasticBeamColumn 475 662 663 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 475

# zero_length_elements zeroLength
element zeroLength 1091 660 662 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1092 663 661 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 476)
node 664 12200 0 11400
rigidLink beam 192 664


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 476)
node 665 15800 0 11400
rigidLink beam 195 665

# Extra nodes for zeroLength
# node tag x y z
node 666 12200 0 11400
node 667 15800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 476 0.0 0.0 1.0
element elasticBeamColumn 476 666 667 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 476

# zero_length_elements zeroLength
element zeroLength 1093 664 666 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1094 667 665 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 141), with Mesh Node = 147 (auxiliary for element 477)
node 668 4200 14500 14700
rigidLink beam 249 668


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 71), with Mesh Node = 77 (auxiliary for element 477)
node 669 7800 14500 14700
rigidLink beam 203 669

# Extra nodes for zeroLength
# node tag x y z
node 670 4200 14500 14700
node 671 7800 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 477 0.0 0.0 1.0
element elasticBeamColumn 477 670 671 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 477

# zero_length_elements zeroLength
element zeroLength 1095 668 670 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1096 671 669 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 73), with Mesh Node = 79 (auxiliary for element 478)
node 672 3800 14500 18000
rigidLink beam 205 672


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 93), with Mesh Node = 99 (auxiliary for element 478)
node 673 200 14500 18000
rigidLink beam 224 673

# Extra nodes for zeroLength
# node tag x y z
node 674 3800 14500 18000
node 675 200 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 478 0.0 0.0 1.0
element elasticBeamColumn 478 674 675 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 478

# zero_length_elements zeroLength
element zeroLength 1097 672 674 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1098 675 673 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 75), with Mesh Node = 81 (auxiliary for element 479)
node 676 4000 9200 18000
rigidLink beam 207 676


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 73), with Mesh Node = 79 (auxiliary for element 479)
node 677 4000 14300 18000
rigidLink beam 205 677

# Extra nodes for zeroLength
# node tag x y z
node 678 4000 9200 18000
node 679 4000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 479 0.0 -0.0 1.0
element elasticBeamColumn 479 678 679 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 479

# zero_length_elements zeroLength
element zeroLength 1099 676 678 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1100 679 677 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 480)
node 680 4000 5700 14700
rigidLink beam 239 680


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 74), with Mesh Node = 80 (auxiliary for element 480)
node 681 4000 8800 14700
rigidLink beam 206 681

# Extra nodes for zeroLength
# node tag x y z
node 682 4000 5700 14700
node 683 4000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 480 0.0 -0.0 1.0
element elasticBeamColumn 480 682 683 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 480

# zero_length_elements zeroLength
element zeroLength 1101 680 682 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1102 683 681 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 481)
node 684 3800 5500 14700
rigidLink beam 239 684

# Extra nodes for zeroLength
# node tag x y z
node 685 0 5500 14700
node 686 3800 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 481 0.0 0.0 1.0
element elasticBeamColumn 481 685 686 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 481

# zero_length_elements zeroLength
element zeroLength 1103 104 685 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1104 686 684 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 142), with Mesh Node = 148 (auxiliary for element 482)
node 687 0 200 14700
rigidLink beam 250 687

# Extra nodes for zeroLength
# node tag x y z
node 688 0 200 14700
node 689 0 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 482 0.0 -0.0 1.0
element elasticBeamColumn 482 688 689 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 482

# zero_length_elements zeroLength
element zeroLength 1105 687 688 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1106 689 104 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 142), with Mesh Node = 148 (auxiliary for element 483)
node 690 200 0 14700
rigidLink beam 250 690


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 483)
node 691 3800 0 14700
rigidLink beam 241 691

# Extra nodes for zeroLength
# node tag x y z
node 692 200 0 14700
node 693 3800 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 483 0.0 0.0 1.0
element elasticBeamColumn 483 692 693 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 483

# zero_length_elements zeroLength
element zeroLength 1107 690 692 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1108 693 691 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 143), with Mesh Node = 149 (auxiliary for element 484)
node 694 200 9000 18000
rigidLink beam 251 694


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 75), with Mesh Node = 81 (auxiliary for element 484)
node 695 3800 9000 18000
rigidLink beam 207 695

# Extra nodes for zeroLength
# node tag x y z
node 696 200 9000 18000
node 697 3800 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 484 0.0 0.0 1.0
element elasticBeamColumn 484 696 697 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 484

# zero_length_elements zeroLength
element zeroLength 1109 694 696 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1110 697 695 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 73), with Mesh Node = 79 (auxiliary for element 485)
node 698 4200 14500 18000
rigidLink beam 205 698


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 72), with Mesh Node = 78 (auxiliary for element 485)
node 699 7800 14500 18000
rigidLink beam 204 699

# Extra nodes for zeroLength
# node tag x y z
node 700 4200 14500 18000
node 701 7800 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 485 0.0 0.0 1.0
element elasticBeamColumn 485 700 701 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 485

# zero_length_elements zeroLength
element zeroLength 1111 698 700 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1112 701 699 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 143), with Mesh Node = 149 (auxiliary for element 486)
node 702 0 9200 18000
rigidLink beam 251 702


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 93), with Mesh Node = 99 (auxiliary for element 486)
node 703 0 14300 18000
rigidLink beam 224 703

# Extra nodes for zeroLength
# node tag x y z
node 704 0 9200 18000
node 705 0 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 486 0.0 -0.0 1.0
element elasticBeamColumn 486 704 705 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 486

# zero_length_elements zeroLength
element zeroLength 1113 702 704 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1114 705 703 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 116), with Mesh Node = 122 (auxiliary for element 487)
node 706 0 5700 11400
rigidLink beam 244 706


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 80), with Mesh Node = 86 (auxiliary for element 487)
node 707 0 8800 11400
rigidLink beam 212 707

# Extra nodes for zeroLength
# node tag x y z
node 708 0 5700 11400
node 709 0 8800 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 487 0.0 -0.0 1.0
element elasticBeamColumn 487 708 709 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 487

# zero_length_elements zeroLength
element zeroLength 1115 706 708 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1116 709 707 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 488)
node 710 8000 9000 8300
rigidLink beam 95 710


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 488)
node 711 8000 9000 11200
rigidLink beam 87 711
# Geometric transformation command
geomTransf PDelta 488 1.0 0.0 -0.0
element forceBeamColumn 488 710 711 488 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 489)
node 712 8000 14500 11600
rigidLink beam 103 712


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 71), with Mesh Node = 77 (auxiliary for element 489)
node 713 8000 14500 14500
rigidLink beam 77 713
# Geometric transformation command
geomTransf PDelta 489 1.0 0.0 -0.0
element forceBeamColumn 489 712 713 489 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 490)
node 714 8000 9000 5000
rigidLink beam 82 714


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 490)
node 715 8000 9000 7900
rigidLink beam 95 715
# Geometric transformation command
geomTransf PDelta 490 1.0 0.0 -0.0
element forceBeamColumn 490 714 715 490 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 10), with Mesh Node = 16 (auxiliary for element 491)
node 716 8000 14500 8300
rigidLink beam 16 716


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 491)
node 717 8000 14500 11200
rigidLink beam 103 717
# Geometric transformation command
geomTransf PDelta 491 1.0 0.0 -0.0
element forceBeamColumn 491 716 717 491 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 492)
node 718 12000 5500 7900
rigidLink beam 58 718
# Geometric transformation command
geomTransf PDelta 492 1.0 0.0 -0.0
element forceBeamColumn 492 59 718 492 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 493)
node 719 12000 200 4800
rigidLink beam 193 719

# Extra nodes for zeroLength
# node tag x y z
node 720 12000 200 4800
node 721 12000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 493 0.0 -0.0 1.0
element elasticBeamColumn 493 720 721 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 493

# zero_length_elements zeroLength
element zeroLength 1117 719 720 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1118 721 59 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 494)
node 722 16200 0 4800
rigidLink beam 196 722


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 494)
node 723 19800 0 4800
rigidLink beam 168 723

# Extra nodes for zeroLength
# node tag x y z
node 724 16200 0 4800
node 725 19800 0 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 494 0.0 0.0 1.0
element elasticBeamColumn 494 724 725 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 494

# zero_length_elements zeroLength
element zeroLength 1119 722 724 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1120 725 723 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 495)
node 726 16000 200 4800
rigidLink beam 196 726


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 495)
node 727 16000 5300 4800
rigidLink beam 171 727

# Extra nodes for zeroLength
# node tag x y z
node 728 16000 200 4800
node 729 16000 5300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 495 0.0 -0.0 1.0
element elasticBeamColumn 495 728 729 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 495

# zero_length_elements zeroLength
element zeroLength 1121 726 728 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1122 729 727 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 496)
node 730 8000 14500 5000
rigidLink beam 31 730


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 10), with Mesh Node = 16 (auxiliary for element 496)
node 731 8000 14500 7900
rigidLink beam 16 731
# Geometric transformation command
geomTransf PDelta 496 1.0 0.0 -0.0
element forceBeamColumn 496 730 731 496 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 497)
node 732 8000 200 4800
rigidLink beam 210 732


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 108), with Mesh Node = 114 (auxiliary for element 497)
node 733 8000 5300 4800
rigidLink beam 237 733

# Extra nodes for zeroLength
# node tag x y z
node 734 8000 200 4800
node 735 8000 5300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 497 0.0 -0.0 1.0
element elasticBeamColumn 497 734 735 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 497

# zero_length_elements zeroLength
element zeroLength 1123 732 734 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1124 735 733 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 498)
node 736 8200 9000 4800
rigidLink beam 208 736


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 3), with Mesh Node = 9 (auxiliary for element 498)
node 737 11800 9000 4800
rigidLink beam 150 737

# Extra nodes for zeroLength
# node tag x y z
node 738 8200 9000 4800
node 739 11800 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 498 0.0 0.0 1.0
element elasticBeamColumn 498 738 739 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 498

# zero_length_elements zeroLength
element zeroLength 1125 736 738 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1126 739 737 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 499)
node 740 15800 5500 4800
rigidLink beam 171 740

# Extra nodes for zeroLength
# node tag x y z
node 741 12000 5500 4800
node 742 15800 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 499 0.0 0.0 1.0
element elasticBeamColumn 499 741 742 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 499

# zero_length_elements zeroLength
element zeroLength 1127 59 741 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1128 742 740 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 500)
node 743 16200 5500 4800
rigidLink beam 171 743

# Extra nodes for zeroLength
# node tag x y z
node 744 16200 5500 4800
node 745 20000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 500 0.0 0.0 1.0
element elasticBeamColumn 500 744 745 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 500

# zero_length_elements zeroLength
element zeroLength 1129 743 744 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1130 745 32 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 3), with Mesh Node = 9 (auxiliary for element 501)
node 746 12000 8800 4800
rigidLink beam 150 746

# Extra nodes for zeroLength
# node tag x y z
node 747 12000 5500 4800
node 748 12000 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 501 0.0 -0.0 1.0
element elasticBeamColumn 501 747 748 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 501

# zero_length_elements zeroLength
element zeroLength 1131 59 747 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1132 748 746 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 76), with Mesh Node = 82 (auxiliary for element 502)
node 749 8000 9200 4800
rigidLink beam 208 749


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 502)
node 750 8000 14300 4800
rigidLink beam 170 750

# Extra nodes for zeroLength
# node tag x y z
node 751 8000 9200 4800
node 752 8000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 502 0.0 -0.0 1.0
element elasticBeamColumn 502 751 752 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 502

# zero_length_elements zeroLength
element zeroLength 1133 749 751 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1134 752 750 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 503)
node 753 20000 200 4800
rigidLink beam 168 753

# Extra nodes for zeroLength
# node tag x y z
node 754 20000 200 4800
node 755 20000 5500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 503 0.0 -0.0 1.0
element elasticBeamColumn 503 754 755 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 503

# zero_length_elements zeroLength
element zeroLength 1135 753 754 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1136 755 32 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 67), with Mesh Node = 73 (auxiliary for element 504)
node 756 8000 200 11400
rigidLink beam 200 756


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 504)
node 757 8000 5300 11400
rigidLink beam 236 757

# Extra nodes for zeroLength
# node tag x y z
node 758 8000 200 11400
node 759 8000 5300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 504 0.0 -0.0 1.0
element elasticBeamColumn 504 758 759 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 504

# zero_length_elements zeroLength
element zeroLength 1137 756 758 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1138 759 757 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 505)
node 760 16000 200 11400
rigidLink beam 195 760


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 41), with Mesh Node = 47 (auxiliary for element 505)
node 761 16000 5300 11400
rigidLink beam 177 761

# Extra nodes for zeroLength
# node tag x y z
node 762 16000 200 11400
node 763 16000 5300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 505 0.0 -0.0 1.0
element elasticBeamColumn 505 762 763 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 505

# zero_length_elements zeroLength
element zeroLength 1139 760 762 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1140 763 761 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 506)
node 764 12000 5700 14700
rigidLink beam 240 764


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 29), with Mesh Node = 35 (auxiliary for element 506)
node 765 12000 8800 14700
rigidLink beam 173 765

# Extra nodes for zeroLength
# node tag x y z
node 766 12000 5700 14700
node 767 12000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 506 0.0 -0.0 1.0
element elasticBeamColumn 506 766 767 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 506

# zero_length_elements zeroLength
element zeroLength 1141 764 766 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1142 767 765 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 507)
node 768 12000 200 11400
rigidLink beam 192 768

# Extra nodes for zeroLength
# node tag x y z
node 769 12000 200 11400
node 770 12000 5500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 507 0.0 -0.0 1.0
element elasticBeamColumn 507 769 770 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 507

# zero_length_elements zeroLength
element zeroLength 1143 768 769 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1144 770 57 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 508)
node 771 16200 0 11400
rigidLink beam 195 771


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 42), with Mesh Node = 48 (auxiliary for element 508)
node 772 19800 0 11400
rigidLink beam 178 772

# Extra nodes for zeroLength
# node tag x y z
node 773 16200 0 11400
node 774 19800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 508 0.0 0.0 1.0
element elasticBeamColumn 508 773 774 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 508

# zero_length_elements zeroLength
element zeroLength 1145 771 773 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1146 774 772 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 29), with Mesh Node = 35 (auxiliary for element 509)
node 775 12000 9200 14700
rigidLink beam 173 775


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 509)
node 776 12000 14300 14700
rigidLink beam 189 776

# Extra nodes for zeroLength
# node tag x y z
node 777 12000 9200 14700
node 778 12000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 509 0.0 -0.0 1.0
element elasticBeamColumn 509 777 778 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 509

# zero_length_elements zeroLength
element zeroLength 1147 775 777 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1148 778 776 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 510)
node 779 12200 5500 14700
rigidLink beam 240 779

# Extra nodes for zeroLength
# node tag x y z
node 780 12200 5500 14700
node 781 16000 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 510 0.0 0.0 1.0
element elasticBeamColumn 510 780 781 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 510

# zero_length_elements zeroLength
element zeroLength 1149 779 780 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1150 781 49 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 511)
node 782 19800 5500 14700
rigidLink beam 182 782

# Extra nodes for zeroLength
# node tag x y z
node 783 16000 5500 14700
node 784 19800 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 511 0.0 0.0 1.0
element elasticBeamColumn 511 783 784 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 511

# zero_length_elements zeroLength
element zeroLength 1151 49 783 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1152 784 782 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 512)
node 785 11800 5500 14700
rigidLink beam 240 785

# Extra nodes for zeroLength
# node tag x y z
node 786 8000 5500 14700
node 787 11800 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 512 0.0 0.0 1.0
element elasticBeamColumn 512 786 787 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 512

# zero_length_elements zeroLength
element zeroLength 1153 93 786 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1154 787 785 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 44), with Mesh Node = 50 (auxiliary for element 513)
node 788 20000 200 14700
rigidLink beam 179 788


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 513)
node 789 20000 5300 14700
rigidLink beam 182 789

# Extra nodes for zeroLength
# node tag x y z
node 790 20000 200 14700
node 791 20000 5300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 513 0.0 -0.0 1.0
element elasticBeamColumn 513 790 791 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 513

# zero_length_elements zeroLength
element zeroLength 1155 788 790 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1156 791 789 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 5), with Mesh Node = 11 (auxiliary for element 514)
node 792 16000 14500 8300
rigidLink beam 11 792


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 514)
node 793 16000 14500 11200
rigidLink beam 28 793
# Geometric transformation command
geomTransf PDelta 514 1.0 0.0 -0.0
element forceBeamColumn 514 792 793 514 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 22), with Mesh Node = 28 (auxiliary for element 515)
node 794 16000 14500 11600
rigidLink beam 28 794


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 515)
node 795 16000 14500 14500
rigidLink beam 52 795
# Geometric transformation command
geomTransf PDelta 515 1.0 0.0 -0.0
element forceBeamColumn 515 794 795 515 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 516)
node 796 16000 14500 14900
rigidLink beam 52 796


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 516)
node 797 16000 14500 17800
rigidLink beam 60 797
# Geometric transformation command
geomTransf PDelta 516 1.0 0.0 -0.0
element forceBeamColumn 516 796 797 516 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 517)
node 798 8000 200 14700
rigidLink beam 219 798

# Extra nodes for zeroLength
# node tag x y z
node 799 8000 200 14700
node 800 8000 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 517 0.0 -0.0 1.0
element elasticBeamColumn 517 799 800 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 517

# zero_length_elements zeroLength
element zeroLength 1157 798 799 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1158 800 93 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 518)
node 801 16200 14500 18000
rigidLink beam 187 801


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 120), with Mesh Node = 126 (auxiliary for element 518)
node 802 19800 14500 18000
rigidLink beam 248 802

# Extra nodes for zeroLength
# node tag x y z
node 803 16200 14500 18000
node 804 19800 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 518 0.0 0.0 1.0
element elasticBeamColumn 518 803 804 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 518

# zero_length_elements zeroLength
element zeroLength 1159 801 803 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1160 804 802 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 519)
node 805 8200 5500 18000
rigidLink beam 238 805

# Extra nodes for zeroLength
# node tag x y z
node 806 8200 5500 18000
node 807 12000 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 519 0.0 0.0 1.0
element elasticBeamColumn 519 806 807 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 519

# zero_length_elements zeroLength
element zeroLength 1161 805 806 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1162 807 118 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 520)
node 808 16000 14300 18000
rigidLink beam 187 808

# Extra nodes for zeroLength
# node tag x y z
node 809 16000 9000 18000
node 810 16000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 520 0.0 -0.0 1.0
element elasticBeamColumn 520 809 810 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 520

# zero_length_elements zeroLength
element zeroLength 1163 23 809 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1164 810 808 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 521)
node 811 16000 5700 18000
rigidLink beam 198 811

# Extra nodes for zeroLength
# node tag x y z
node 812 16000 5700 18000
node 813 16000 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 521 0.0 -0.0 1.0
element elasticBeamColumn 521 812 813 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 521

# zero_length_elements zeroLength
element zeroLength 1165 811 812 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1166 813 23 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 522)
node 814 12000 8800 18000
rigidLink beam 176 814

# Extra nodes for zeroLength
# node tag x y z
node 815 12000 5500 18000
node 816 12000 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 522 0.0 -0.0 1.0
element elasticBeamColumn 522 815 816 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 522

# zero_length_elements zeroLength
element zeroLength 1167 118 815 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1168 816 814 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 523)
node 817 15800 5500 18000
rigidLink beam 198 817

# Extra nodes for zeroLength
# node tag x y z
node 818 12000 5500 18000
node 819 15800 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 523 0.0 0.0 1.0
element elasticBeamColumn 523 818 819 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 523

# zero_length_elements zeroLength
element zeroLength 1169 118 818 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1170 819 817 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 31), with Mesh Node = 37 (auxiliary for element 524)
node 820 20000 9200 18000
rigidLink beam 175 820


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 120), with Mesh Node = 126 (auxiliary for element 524)
node 821 20000 14300 18000
rigidLink beam 248 821

# Extra nodes for zeroLength
# node tag x y z
node 822 20000 9200 18000
node 823 20000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 524 0.0 -0.0 1.0
element elasticBeamColumn 524 822 823 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 524

# zero_length_elements zeroLength
element zeroLength 1171 820 822 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1172 823 821 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 12), with Mesh Node = 18 (auxiliary for element 525)
node 824 12000 9200 8100
rigidLink beam 159 824


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 4), with Mesh Node = 10 (auxiliary for element 525)
node 825 12000 14300 8100
rigidLink beam 151 825

# Extra nodes for zeroLength
# node tag x y z
node 826 12000 9200 8100
node 827 12000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 525 0.0 -0.0 1.0
element elasticBeamColumn 525 826 827 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 525

# zero_length_elements zeroLength
element zeroLength 1173 824 826 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1174 827 825 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 526)
node 828 20000 5700 18000
rigidLink beam 185 828


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 31), with Mesh Node = 37 (auxiliary for element 526)
node 829 20000 8800 18000
rigidLink beam 175 829

# Extra nodes for zeroLength
# node tag x y z
node 830 20000 5700 18000
node 831 20000 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 526 0.0 -0.0 1.0
element elasticBeamColumn 526 830 831 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 526

# zero_length_elements zeroLength
element zeroLength 1175 828 830 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1176 831 829 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 527)
node 832 16200 5500 18000
rigidLink beam 198 832


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 527)
node 833 19800 5500 18000
rigidLink beam 185 833

# Extra nodes for zeroLength
# node tag x y z
node 834 16200 5500 18000
node 835 19800 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 527 0.0 0.0 1.0
element elasticBeamColumn 527 834 835 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 527

# zero_length_elements zeroLength
element zeroLength 1177 832 834 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1178 835 833 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 5), with Mesh Node = 11 (auxiliary for element 528)
node 836 16200 14500 8100
rigidLink beam 152 836


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 68), with Mesh Node = 74 (auxiliary for element 528)
node 837 19800 14500 8100
rigidLink beam 201 837

# Extra nodes for zeroLength
# node tag x y z
node 838 16200 14500 8100
node 839 19800 14500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 528 0.0 0.0 1.0
element elasticBeamColumn 528 838 839 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 528

# zero_length_elements zeroLength
element zeroLength 1179 836 838 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1180 839 837 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 7), with Mesh Node = 13 (auxiliary for element 529)
node 840 12000 14500 11600
rigidLink beam 13 840


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 529)
node 841 12000 14500 14500
rigidLink beam 62 841
# Geometric transformation command
geomTransf PDelta 529 1.0 0.0 -0.0
element forceBeamColumn 529 840 841 529 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 69), with Mesh Node = 75 (auxiliary for element 530)
node 842 8000 200 18000
rigidLink beam 202 842


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 530)
node 843 8000 5300 18000
rigidLink beam 238 843

# Extra nodes for zeroLength
# node tag x y z
node 844 8000 200 18000
node 845 8000 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 530 0.0 -0.0 1.0
element elasticBeamColumn 530 844 845 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 530

# zero_length_elements zeroLength
element zeroLength 1181 842 844 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1182 845 843 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 11), with Mesh Node = 17 (auxiliary for element 531)
node 846 20000 9200 8100
rigidLink beam 158 846


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 68), with Mesh Node = 74 (auxiliary for element 531)
node 847 20000 14300 8100
rigidLink beam 201 847

# Extra nodes for zeroLength
# node tag x y z
node 848 20000 9200 8100
node 849 20000 14300 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 531 0.0 -0.0 1.0
element elasticBeamColumn 531 848 849 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 531

# zero_length_elements zeroLength
element zeroLength 1183 846 848 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1184 849 847 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 532)
node 850 8200 14500 11400
rigidLink beam 228 850


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 7), with Mesh Node = 13 (auxiliary for element 532)
node 851 11800 14500 11400
rigidLink beam 154 851

# Extra nodes for zeroLength
# node tag x y z
node 852 8200 14500 11400
node 853 11800 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 532 0.0 0.0 1.0
element elasticBeamColumn 532 852 853 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 532

# zero_length_elements zeroLength
element zeroLength 1185 850 852 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1186 853 851 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 533)
node 854 8000 0 14900
rigidLink beam 94 854


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 69), with Mesh Node = 75 (auxiliary for element 533)
node 855 8000 0 17800
rigidLink beam 75 855
# Geometric transformation command
geomTransf PDelta 533 1.0 0.0 -0.0
element forceBeamColumn 533 854 855 533 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 14), with Mesh Node = 20 (auxiliary for element 534)
node 856 20000 5500 7900
rigidLink beam 20 856
# Geometric transformation command
geomTransf PDelta 534 1.0 0.0 -0.0
element forceBeamColumn 534 32 856 534 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 27), with Mesh Node = 33 (auxiliary for element 535)
node 857 16000 5500 5000
rigidLink beam 33 857
# Geometric transformation command
geomTransf PDelta 535 1.0 0.0 -0.0
element forceBeamColumn 535 857 19 535 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 67), with Mesh Node = 73 (auxiliary for element 536)
node 858 8000 0 11600
rigidLink beam 73 858


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 536)
node 859 8000 0 14500
rigidLink beam 94 859
# Geometric transformation command
geomTransf PDelta 536 1.0 0.0 -0.0
element forceBeamColumn 536 858 859 536 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 537)
node 860 20000 5500 14900
rigidLink beam 53 860


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 50), with Mesh Node = 56 (auxiliary for element 537)
node 861 20000 5500 17800
rigidLink beam 56 861
# Geometric transformation command
geomTransf PDelta 537 1.0 0.0 -0.0
element forceBeamColumn 537 860 861 537 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 47), with Mesh Node = 53 (auxiliary for element 538)
node 862 20000 5500 14500
rigidLink beam 53 862
# Geometric transformation command
geomTransf PDelta 538 1.0 0.0 -0.0
element forceBeamColumn 538 46 862 538 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 52), with Mesh Node = 58 (auxiliary for element 539)
node 863 12200 5500 8100
rigidLink beam 186 863

# Extra nodes for zeroLength
# node tag x y z
node 864 12200 5500 8100
node 865 16000 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 539 0.0 0.0 1.0
element elasticBeamColumn 539 864 865 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 539

# zero_length_elements zeroLength
element zeroLength 1187 863 864 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1188 865 19 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 89), with Mesh Node = 95 (auxiliary for element 540)
node 866 8200 9000 8100
rigidLink beam 220 866


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 12), with Mesh Node = 18 (auxiliary for element 540)
node 867 11800 9000 8100
rigidLink beam 159 867

# Extra nodes for zeroLength
# node tag x y z
node 868 8200 9000 8100
node 869 11800 9000 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 540 0.0 0.0 1.0
element elasticBeamColumn 540 868 869 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 540

# zero_length_elements zeroLength
element zeroLength 1189 866 868 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1190 869 867 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 14), with Mesh Node = 20 (auxiliary for element 541)
node 870 19800 5500 8100
rigidLink beam 160 870

# Extra nodes for zeroLength
# node tag x y z
node 871 16000 5500 8100
node 872 19800 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 541 0.0 0.0 1.0
element elasticBeamColumn 541 871 872 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 541

# zero_length_elements zeroLength
element zeroLength 1191 19 871 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1192 872 870 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 542)
node 873 16200 0 8100
rigidLink beam 162 873


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 15), with Mesh Node = 21 (auxiliary for element 542)
node 874 19800 0 8100
rigidLink beam 161 874

# Extra nodes for zeroLength
# node tag x y z
node 875 16200 0 8100
node 876 19800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 542 0.0 0.0 1.0
element elasticBeamColumn 542 875 876 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 542

# zero_length_elements zeroLength
element zeroLength 1193 873 875 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1194 876 874 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 83), with Mesh Node = 89 (auxiliary for element 543)
node 877 4200 0 8100
rigidLink beam 215 877


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 543)
node 878 7800 0 8100
rigidLink beam 199 878

# Extra nodes for zeroLength
# node tag x y z
node 879 4200 0 8100
node 880 7800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 543 0.0 0.0 1.0
element elasticBeamColumn 543 879 880 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 543

# zero_length_elements zeroLength
element zeroLength 1195 877 879 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1196 880 878 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 544)
node 881 12200 0 8100
rigidLink beam 194 881


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 16), with Mesh Node = 22 (auxiliary for element 544)
node 882 15800 0 8100
rigidLink beam 162 882

# Extra nodes for zeroLength
# node tag x y z
node 883 12200 0 8100
node 884 15800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 544 0.0 0.0 1.0
element elasticBeamColumn 544 883 884 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 544

# zero_length_elements zeroLength
element zeroLength 1197 881 883 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1198 884 882 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 66), with Mesh Node = 72 (auxiliary for element 545)
node 885 8200 0 8100
rigidLink beam 199 885


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 61), with Mesh Node = 67 (auxiliary for element 545)
node 886 11800 0 8100
rigidLink beam 194 886

# Extra nodes for zeroLength
# node tag x y z
node 887 8200 0 8100
node 888 11800 0 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 545 0.0 0.0 1.0
element elasticBeamColumn 545 887 888 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 545

# zero_length_elements zeroLength
element zeroLength 1199 885 887 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1200 888 886 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 71), with Mesh Node = 77 (auxiliary for element 546)
node 889 8000 14500 14900
rigidLink beam 77 889


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 72), with Mesh Node = 78 (auxiliary for element 546)
node 890 8000 14500 17800
rigidLink beam 78 890
# Geometric transformation command
geomTransf PDelta 546 1.0 0.0 -0.0
element forceBeamColumn 546 889 890 546 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 30), with Mesh Node = 36 (auxiliary for element 547)
node 891 8000 9000 14900
rigidLink beam 36 891


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 547)
node 892 8000 9000 17800
rigidLink beam 70 892
# Geometric transformation command
geomTransf PDelta 547 1.0 0.0 -0.0
element forceBeamColumn 547 891 892 547 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 81), with Mesh Node = 87 (auxiliary for element 548)
node 893 8000 9000 11600
rigidLink beam 87 893


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 30), with Mesh Node = 36 (auxiliary for element 548)
node 894 8000 9000 14500
rigidLink beam 36 894
# Geometric transformation command
geomTransf PDelta 548 1.0 0.0 -0.0
element forceBeamColumn 548 893 894 548 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 141), with Mesh Node = 147 (auxiliary for element 549)
node 895 3800 14500 14700
rigidLink beam 249 895


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 549)
node 896 200 14500 14700
rigidLink beam 226 896

# Extra nodes for zeroLength
# node tag x y z
node 897 3800 14500 14700
node 898 200 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 549 0.0 0.0 1.0
element elasticBeamColumn 549 897 898 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 549

# zero_length_elements zeroLength
element zeroLength 1201 895 897 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1202 898 896 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 110), with Mesh Node = 116 (auxiliary for element 550)
node 899 4000 5500 14900
rigidLink beam 116 899


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 550)
node 900 4000 5500 17800
rigidLink beam 120 900
# Geometric transformation command
geomTransf PDelta 550 1.0 0.0 -0.0
element forceBeamColumn 550 899 900 550 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 74), with Mesh Node = 80 (auxiliary for element 551)
node 901 4000 9000 14900
rigidLink beam 80 901


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 75), with Mesh Node = 81 (auxiliary for element 551)
node 902 4000 9000 17800
rigidLink beam 81 902
# Geometric transformation command
geomTransf PDelta 551 1.0 0.0 -0.0
element forceBeamColumn 551 901 902 551 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 75), with Mesh Node = 81 (auxiliary for element 552)
node 903 4200 9000 18000
rigidLink beam 207 903


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 552)
node 904 7800 9000 18000
rigidLink beam 197 904

# Extra nodes for zeroLength
# node tag x y z
node 905 4200 9000 18000
node 906 7800 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 552 0.0 0.0 1.0
element elasticBeamColumn 552 905 906 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 552

# zero_length_elements zeroLength
element zeroLength 1203 903 905 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1204 906 904 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 553)
node 907 4000 14300 4800
rigidLink beam 231 907

# Extra nodes for zeroLength
# node tag x y z
node 908 4000 9000 4800
node 909 4000 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 553 0.0 -0.0 1.0
element elasticBeamColumn 553 908 909 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 553

# zero_length_elements zeroLength
element zeroLength 1205 130 908 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1206 909 907 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 554)
node 910 0 5700 4800
rigidLink beam 246 910


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 554)
node 911 0 8800 4800
rigidLink beam 221 911

# Extra nodes for zeroLength
# node tag x y z
node 912 0 5700 4800
node 913 0 8800 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 554 0.0 -0.0 1.0
element elasticBeamColumn 554 912 913 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 554

# zero_length_elements zeroLength
element zeroLength 1207 910 912 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1208 913 911 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 80), with Mesh Node = 86 (auxiliary for element 555)
node 914 0 9200 11400
rigidLink beam 212 914


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 555)
node 915 0 14300 11400
rigidLink beam 227 915

# Extra nodes for zeroLength
# node tag x y z
node 916 0 9200 11400
node 917 0 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 555 0.0 -0.0 1.0
element elasticBeamColumn 555 916 917 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 555

# zero_length_elements zeroLength
element zeroLength 1209 914 916 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1210 917 915 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 556)
node 918 200 9000 4800
rigidLink beam 221 918

# Extra nodes for zeroLength
# node tag x y z
node 919 200 9000 4800
node 920 4000 9000 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 556 0.0 0.0 1.0
element elasticBeamColumn 556 919 920 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 556

# zero_length_elements zeroLength
element zeroLength 1211 918 919 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1212 920 130 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 90), with Mesh Node = 96 (auxiliary for element 557)
node 921 0 9200 4800
rigidLink beam 221 921


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 102), with Mesh Node = 108 (auxiliary for element 557)
node 922 0 14300 4800
rigidLink beam 232 922

# Extra nodes for zeroLength
# node tag x y z
node 923 0 9200 4800
node 924 0 14300 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 557 0.0 -0.0 1.0
element elasticBeamColumn 557 923 924 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 557

# zero_length_elements zeroLength
element zeroLength 1213 921 923 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1214 924 922 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 558)
node 925 3800 14500 4800
rigidLink beam 231 925


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 102), with Mesh Node = 108 (auxiliary for element 558)
node 926 200 14500 4800
rigidLink beam 232 926

# Extra nodes for zeroLength
# node tag x y z
node 927 3800 14500 4800
node 928 200 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 558 0.0 0.0 1.0
element elasticBeamColumn 558 927 928 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 558

# zero_length_elements zeroLength
element zeroLength 1215 925 927 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1216 928 926 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 116), with Mesh Node = 122 (auxiliary for element 559)
node 929 0 5500 11600
rigidLink beam 122 929
# Geometric transformation command
geomTransf PDelta 559 1.0 0.0 -0.0
element forceBeamColumn 559 929 104 559 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 560)
node 930 0 14500 14900
rigidLink beam 101 930


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 93), with Mesh Node = 99 (auxiliary for element 560)
node 931 0 14500 17800
rigidLink beam 99 931
# Geometric transformation command
geomTransf PDelta 560 1.0 0.0 -0.0
element forceBeamColumn 560 930 931 560 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 561)
node 932 0 9000 8300
rigidLink beam 109 932


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 80), with Mesh Node = 86 (auxiliary for element 561)
node 933 0 9000 11200
rigidLink beam 86 933
# Geometric transformation command
geomTransf PDelta 561 1.0 0.0 -0.0
element forceBeamColumn 561 932 933 561 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 118), with Mesh Node = 124 (auxiliary for element 562)
node 934 0 5500 5000
rigidLink beam 124 934
# Geometric transformation command
geomTransf PDelta 562 1.0 0.0 -0.0
element forceBeamColumn 562 934 146 562 HingeRadau 6 200.0 6 200.0 7


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 563)
node 935 0 9000 14900
rigidLink beam 98 935


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 143), with Mesh Node = 149 (auxiliary for element 563)
node 936 0 9000 17800
rigidLink beam 149 936
# Geometric transformation command
geomTransf PDelta 563 1.0 0.0 -0.0
element forceBeamColumn 563 935 936 563 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 116), with Mesh Node = 122 (auxiliary for element 564)
node 937 0 5500 11200
rigidLink beam 122 937
# Geometric transformation command
geomTransf PDelta 564 1.0 0.0 -0.0
element forceBeamColumn 564 146 937 564 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 565)
node 938 0 0 8300
rigidLink beam 91 938


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 84), with Mesh Node = 90 (auxiliary for element 565)
node 939 0 0 11200
rigidLink beam 90 939
# Geometric transformation command
geomTransf PDelta 565 1.0 0.0 -0.0
element forceBeamColumn 565 938 939 565 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 142), with Mesh Node = 148 (auxiliary for element 566)
node 940 0 0 14900
rigidLink beam 148 940


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 104), with Mesh Node = 110 (auxiliary for element 566)
node 941 0 0 17800
rigidLink beam 110 941
# Geometric transformation command
geomTransf PDelta 566 1.0 0.0 -0.0
element forceBeamColumn 566 940 941 566 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 115), with Mesh Node = 121 (auxiliary for element 567)
node 942 0 5500 17800
rigidLink beam 121 942
# Geometric transformation command
geomTransf PDelta 567 1.0 0.0 -0.0
element forceBeamColumn 567 104 942 567 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 105), with Mesh Node = 111 (auxiliary for element 568)
node 943 0 0 5000
rigidLink beam 111 943


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 568)
node 944 0 0 7900
rigidLink beam 91 944
# Geometric transformation command
geomTransf PDelta 568 1.0 0.0 -0.0
element forceBeamColumn 568 943 944 568 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 569)
node 945 3800 14500 11400
rigidLink beam 225 945


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 569)
node 946 200 14500 11400
rigidLink beam 227 946

# Extra nodes for zeroLength
# node tag x y z
node 947 3800 14500 11400
node 948 200 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 569 0.0 0.0 1.0
element elasticBeamColumn 569 947 948 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 569

# zero_length_elements zeroLength
element zeroLength 1217 945 947 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1218 948 946 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 84), with Mesh Node = 90 (auxiliary for element 570)
node 949 0 0 11600
rigidLink beam 90 949


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 142), with Mesh Node = 148 (auxiliary for element 570)
node 950 0 0 14500
rigidLink beam 148 950
# Geometric transformation command
geomTransf PDelta 570 1.0 0.0 -0.0
element forceBeamColumn 570 949 950 570 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 571)
node 951 4000 9200 11400
rigidLink beam 222 951


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 571)
node 952 4000 14300 11400
rigidLink beam 225 952

# Extra nodes for zeroLength
# node tag x y z
node 953 4000 9200 11400
node 954 4000 14300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 571 0.0 -0.0 1.0
element elasticBeamColumn 571 953 954 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 571

# zero_length_elements zeroLength
element zeroLength 1219 951 953 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1220 954 952 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 80), with Mesh Node = 86 (auxiliary for element 572)
node 955 200 9000 11400
rigidLink beam 212 955


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 91), with Mesh Node = 97 (auxiliary for element 572)
node 956 3800 9000 11400
rigidLink beam 222 956

# Extra nodes for zeroLength
# node tag x y z
node 957 200 9000 11400
node 958 3800 9000 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 572 0.0 0.0 1.0
element elasticBeamColumn 572 957 958 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 572

# zero_length_elements zeroLength
element zeroLength 1221 955 957 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1222 958 956 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 57), with Mesh Node = 63 (auxiliary for element 573)
node 959 12000 9000 11600
rigidLink beam 63 959


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 29), with Mesh Node = 35 (auxiliary for element 573)
node 960 12000 9000 14500
rigidLink beam 35 960
# Geometric transformation command
geomTransf PDelta 573 1.0 0.0 -0.0
element forceBeamColumn 573 959 960 573 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 20), with Mesh Node = 26 (auxiliary for element 574)
node 961 20000 9000 14900
rigidLink beam 26 961


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 31), with Mesh Node = 37 (auxiliary for element 574)
node 962 20000 9000 17800
rigidLink beam 37 962
# Geometric transformation command
geomTransf PDelta 574 1.0 0.0 -0.0
element forceBeamColumn 574 961 962 574 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 29), with Mesh Node = 35 (auxiliary for element 575)
node 963 12000 9000 14900
rigidLink beam 35 963


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 575)
node 964 12000 9000 17800
rigidLink beam 38 964
# Geometric transformation command
geomTransf PDelta 575 1.0 0.0 -0.0
element forceBeamColumn 575 963 964 575 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 106), with Mesh Node = 112 (auxiliary for element 576)
node 965 8000 5500 11600
rigidLink beam 112 965
# Geometric transformation command
geomTransf PDelta 576 1.0 0.0 -0.0
element forceBeamColumn 576 965 93 576 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 577)
node 966 8000 5500 17800
rigidLink beam 115 966
# Geometric transformation command
geomTransf PDelta 577 1.0 0.0 -0.0
element forceBeamColumn 577 93 966 577 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 68), with Mesh Node = 74 (auxiliary for element 578)
node 967 20000 14500 8300
rigidLink beam 74 967


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 578)
node 968 20000 14500 11200
rigidLink beam 27 968
# Geometric transformation command
geomTransf PDelta 578 1.0 0.0 -0.0
element forceBeamColumn 578 967 968 578 HingeRadau 14 225.0 14 225.0 17


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 21), with Mesh Node = 27 (auxiliary for element 579)
node 969 20000 14500 11600
rigidLink beam 27 969


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 48), with Mesh Node = 54 (auxiliary for element 579)
node 970 20000 14500 14500
rigidLink beam 54 970
# Geometric transformation command
geomTransf PDelta 579 1.0 0.0 -0.0
element forceBeamColumn 579 969 970 579 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 580)
node 971 12000 14500 14900
rigidLink beam 62 971


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 580)
node 972 12000 14500 17800
rigidLink beam 55 972
# Geometric transformation command
geomTransf PDelta 580 1.0 0.0 -0.0
element forceBeamColumn 580 971 972 580 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 581)
node 973 20000 14500 5000
rigidLink beam 34 973


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 68), with Mesh Node = 74 (auxiliary for element 581)
node 974 20000 14500 7900
rigidLink beam 74 974
# Geometric transformation command
geomTransf PDelta 581 1.0 0.0 -0.0
element forceBeamColumn 581 973 974 581 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 44), with Mesh Node = 50 (auxiliary for element 582)
node 975 19800 0 14700
rigidLink beam 179 975


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 582)
node 976 16200 0 14700
rigidLink beam 191 976

# Extra nodes for zeroLength
# node tag x y z
node 977 19800 0 14700
node 978 16200 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 582 0.0 0.0 1.0
element elasticBeamColumn 582 977 978 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 582

# zero_length_elements zeroLength
element zeroLength 1223 975 977 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0
element zeroLength 1224 978 976 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient -1.0 0.0 0.0 0.0 -1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 583)
node 979 12000 200 14700
rigidLink beam 188 979


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 111), with Mesh Node = 117 (auxiliary for element 583)
node 980 12000 5300 14700
rigidLink beam 240 980

# Extra nodes for zeroLength
# node tag x y z
node 981 12000 200 14700
node 982 12000 5300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 583 0.0 -0.0 1.0
element elasticBeamColumn 583 981 982 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 583

# zero_length_elements zeroLength
element zeroLength 1225 979 981 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1226 982 980 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 584)
node 983 12200 0 14700
rigidLink beam 188 983


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 584)
node 984 15800 0 14700
rigidLink beam 191 984

# Extra nodes for zeroLength
# node tag x y z
node 985 12200 0 14700
node 986 15800 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 584 0.0 0.0 1.0
element elasticBeamColumn 584 985 986 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 584

# zero_length_elements zeroLength
element zeroLength 1227 983 985 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1228 986 984 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 585)
node 987 16000 200 14700
rigidLink beam 191 987

# Extra nodes for zeroLength
# node tag x y z
node 988 16000 200 14700
node 989 16000 5500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 585 0.0 -0.0 1.0
element elasticBeamColumn 585 988 989 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 585

# zero_length_elements zeroLength
element zeroLength 1229 987 988 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1230 989 49 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 48), with Mesh Node = 54 (auxiliary for element 586)
node 990 20000 14500 14900
rigidLink beam 54 990


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 120), with Mesh Node = 126 (auxiliary for element 586)
node 991 20000 14500 17800
rigidLink beam 126 991
# Geometric transformation command
geomTransf PDelta 586 1.0 0.0 -0.0
element forceBeamColumn 586 990 991 586 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 587)
node 992 12000 200 18000
rigidLink beam 209 992

# Extra nodes for zeroLength
# node tag x y z
node 993 12000 200 18000
node 994 12000 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 587 0.0 -0.0 1.0
element elasticBeamColumn 587 993 994 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 587

# zero_length_elements zeroLength
element zeroLength 1231 992 993 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1232 994 118 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 59), with Mesh Node = 65 (auxiliary for element 588)
node 995 12000 0 11600
rigidLink beam 65 995


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 588)
node 996 12000 0 14500
rigidLink beam 61 996
# Geometric transformation command
geomTransf PDelta 588 1.0 0.0 -0.0
element forceBeamColumn 588 995 996 588 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 589)
node 997 16000 5300 18000
rigidLink beam 198 997

# Extra nodes for zeroLength
# node tag x y z
node 998 16000 0 18000
node 999 16000 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 589 0.0 -0.0 1.0
element elasticBeamColumn 589 998 999 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 589

# zero_length_elements zeroLength
element zeroLength 1233 76 998 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1234 999 997 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 65), with Mesh Node = 71 (auxiliary for element 590)
node 1000 16000 5500 17800
rigidLink beam 71 1000
# Geometric transformation command
geomTransf PDelta 590 1.0 0.0 -0.0
element forceBeamColumn 590 49 1000 590 HingeRadau 18 225.0 18 225.0 19


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 591)
node 1001 12200 0 18000
rigidLink beam 209 1001

# Extra nodes for zeroLength
# node tag x y z
node 1002 12200 0 18000
node 1003 16000 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 591 0.0 0.0 1.0
element elasticBeamColumn 591 1002 1003 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 591

# zero_length_elements zeroLength
element zeroLength 1235 1001 1002 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1236 1003 76 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 592)
node 1004 12000 0 14900
rigidLink beam 61 1004


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 592)
node 1005 12000 0 17800
rigidLink beam 83 1005
# Geometric transformation command
geomTransf PDelta 592 1.0 0.0 -0.0
element forceBeamColumn 592 1004 1005 592 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 45), with Mesh Node = 51 (auxiliary for element 593)
node 1006 19800 0 18000
rigidLink beam 180 1006

# Extra nodes for zeroLength
# node tag x y z
node 1007 16000 0 18000
node 1008 19800 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 593 0.0 0.0 1.0
element elasticBeamColumn 593 1007 1008 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 593

# zero_length_elements zeroLength
element zeroLength 1237 76 1007 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1238 1008 1006 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 69), with Mesh Node = 75 (auxiliary for element 594)
node 1009 8200 0 18000
rigidLink beam 202 1009


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 77), with Mesh Node = 83 (auxiliary for element 594)
node 1010 11800 0 18000
rigidLink beam 209 1010

# Extra nodes for zeroLength
# node tag x y z
node 1011 8200 0 18000
node 1012 11800 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 594 0.0 0.0 1.0
element elasticBeamColumn 594 1011 1012 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 594

# zero_length_elements zeroLength
element zeroLength 1239 1009 1011 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1240 1012 1010 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 88), with Mesh Node = 94 (auxiliary for element 595)
node 1013 8200 0 14700
rigidLink beam 219 1013


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 55), with Mesh Node = 61 (auxiliary for element 595)
node 1014 11800 0 14700
rigidLink beam 188 1014

# Extra nodes for zeroLength
# node tag x y z
node 1015 8200 0 14700
node 1016 11800 0 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 595 0.0 0.0 1.0
element elasticBeamColumn 595 1015 1016 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 595

# zero_length_elements zeroLength
element zeroLength 1241 1013 1015 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1242 1016 1014 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 62), with Mesh Node = 68 (auxiliary for element 596)
node 1017 16000 0 11600
rigidLink beam 68 1017


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 596)
node 1018 16000 0 14500
rigidLink beam 64 1018
# Geometric transformation command
geomTransf PDelta 596 1.0 0.0 -0.0
element forceBeamColumn 596 1017 1018 596 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 24), with Mesh Node = 30 (auxiliary for element 597)
node 1019 16200 14500 4800
rigidLink beam 169 1019


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 28), with Mesh Node = 34 (auxiliary for element 597)
node 1020 19800 14500 4800
rigidLink beam 172 1020

# Extra nodes for zeroLength
# node tag x y z
node 1021 16200 14500 4800
node 1022 19800 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 597 0.0 0.0 1.0
element elasticBeamColumn 597 1021 1022 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 597

# zero_length_elements zeroLength
element zeroLength 1243 1019 1021 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1244 1022 1020 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 60), with Mesh Node = 66 (auxiliary for element 598)
node 1023 12000 0 4600
rigidLink beam 66 1023
# Geometric transformation command
geomTransf PDelta 598 1.0 0.0 -0.0
element forceBeamColumn 598 142 1023 598 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 23), with Mesh Node = 29 (auxiliary for element 599)
node 1024 20000 0 4600
rigidLink beam 29 1024
# Geometric transformation command
geomTransf PDelta 599 1.0 0.0 -0.0
element forceBeamColumn 599 144 1024 599 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 58), with Mesh Node = 64 (auxiliary for element 600)
node 1025 16000 0 14900
rigidLink beam 64 1025
# Geometric transformation command
geomTransf PDelta 600 1.0 0.0 -0.0
element forceBeamColumn 600 1025 76 600 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 78), with Mesh Node = 84 (auxiliary for element 601)
node 1026 8000 0 4600
rigidLink beam 84 1026
# Geometric transformation command
geomTransf PDelta 601 1.0 0.0 -0.0
element forceBeamColumn 601 133 1026 601 HingeRadau 20 225.0 20 225.0 21
# Geometric transformation command
geomTransf PDelta 602 1.0 0.0 -0.0
element forceBeamColumn 602 137 32 602 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 63), with Mesh Node = 69 (auxiliary for element 603)
node 1027 16000 0 4600
rigidLink beam 69 1027
# Geometric transformation command
geomTransf PDelta 603 1.0 0.0 -0.0
element forceBeamColumn 603 141 1027 603 HingeRadau 20 225.0 20 225.0 21


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 101), with Mesh Node = 107 (auxiliary for element 604)
node 1028 4200 14500 4800
rigidLink beam 231 1028


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 25), with Mesh Node = 31 (auxiliary for element 604)
node 1029 7800 14500 4800
rigidLink beam 170 1029

# Extra nodes for zeroLength
# node tag x y z
node 1030 4200 14500 4800
node 1031 7800 14500 4800

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 604 0.0 0.0 1.0
element elasticBeamColumn 604 1030 1031 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 604

# zero_length_elements zeroLength
element zeroLength 1245 1028 1030 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1246 1031 1029 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 84), with Mesh Node = 90 (auxiliary for element 605)
node 1032 0 200 11400
rigidLink beam 216 1032


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 116), with Mesh Node = 122 (auxiliary for element 605)
node 1033 0 5300 11400
rigidLink beam 244 1033

# Extra nodes for zeroLength
# node tag x y z
node 1034 0 200 11400
node 1035 0 5300 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 605 0.0 -0.0 1.0
element elasticBeamColumn 605 1034 1035 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 605

# zero_length_elements zeroLength
element zeroLength 1247 1032 1034 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1248 1035 1033 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 84), with Mesh Node = 90 (auxiliary for element 606)
node 1036 200 0 11400
rigidLink beam 216 1036


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 606)
node 1037 3800 0 11400
rigidLink beam 214 1037

# Extra nodes for zeroLength
# node tag x y z
node 1038 200 0 11400
node 1039 3800 0 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 606 0.0 0.0 1.0
element elasticBeamColumn 606 1038 1039 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 606

# zero_length_elements zeroLength
element zeroLength 1249 1036 1038 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1250 1039 1037 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 94), with Mesh Node = 100 (auxiliary for element 607)
node 1040 4200 14500 11400
rigidLink beam 225 1040


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 97), with Mesh Node = 103 (auxiliary for element 607)
node 1041 7800 14500 11400
rigidLink beam 228 1041

# Extra nodes for zeroLength
# node tag x y z
node 1042 4200 14500 11400
node 1043 7800 14500 11400

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 607 0.0 0.0 1.0
element elasticBeamColumn 607 1042 1043 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 607

# zero_length_elements zeroLength
element zeroLength 1251 1040 1042 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1252 1043 1041 -mat 5 5 5 5 22 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 608)
node 1044 4000 0 14900
rigidLink beam 119 1044


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 608)
node 1045 4000 0 17800
rigidLink beam 125 1045
# Geometric transformation command
geomTransf PDelta 608 1.0 0.0 -0.0
element forceBeamColumn 608 1044 1045 608 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 609)
node 1046 4000 5700 18000
rigidLink beam 242 1046


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 75), with Mesh Node = 81 (auxiliary for element 609)
node 1047 4000 8800 18000
rigidLink beam 207 1047

# Extra nodes for zeroLength
# node tag x y z
node 1048 4000 5700 18000
node 1049 4000 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 609 0.0 -0.0 1.0
element elasticBeamColumn 609 1048 1049 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 609

# zero_length_elements zeroLength
element zeroLength 1253 1046 1048 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1254 1049 1047 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 104), with Mesh Node = 110 (auxiliary for element 610)
node 1050 0 200 18000
rigidLink beam 234 1050


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 115), with Mesh Node = 121 (auxiliary for element 610)
node 1051 0 5300 18000
rigidLink beam 243 1051

# Extra nodes for zeroLength
# node tag x y z
node 1052 0 200 18000
node 1053 0 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 610 0.0 -0.0 1.0
element elasticBeamColumn 610 1052 1053 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 610

# zero_length_elements zeroLength
element zeroLength 1255 1050 1052 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1256 1053 1051 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 115), with Mesh Node = 121 (auxiliary for element 611)
node 1054 0 5700 18000
rigidLink beam 243 1054


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 143), with Mesh Node = 149 (auxiliary for element 611)
node 1055 0 8800 18000
rigidLink beam 251 1055

# Extra nodes for zeroLength
# node tag x y z
node 1056 0 5700 18000
node 1057 0 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 611 0.0 -0.0 1.0
element elasticBeamColumn 611 1056 1057 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 611

# zero_length_elements zeroLength
element zeroLength 1257 1054 1056 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1258 1057 1055 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 115), with Mesh Node = 121 (auxiliary for element 612)
node 1058 200 5500 18000
rigidLink beam 243 1058


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 612)
node 1059 3800 5500 18000
rigidLink beam 242 1059

# Extra nodes for zeroLength
# node tag x y z
node 1060 200 5500 18000
node 1061 3800 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 612 0.0 0.0 1.0
element elasticBeamColumn 612 1060 1061 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 612

# zero_length_elements zeroLength
element zeroLength 1259 1058 1060 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1260 1061 1059 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 85), with Mesh Node = 91 (auxiliary for element 613)
node 1062 0 200 8100
rigidLink beam 217 1062

# Extra nodes for zeroLength
# node tag x y z
node 1063 0 200 8100
node 1064 0 5500 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 613 0.0 -0.0 1.0
element elasticBeamColumn 613 1063 1064 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 613

# zero_length_elements zeroLength
element zeroLength 1261 1062 1063 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1262 1064 146 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 103), with Mesh Node = 109 (auxiliary for element 614)
node 1065 0 8800 8100
rigidLink beam 233 1065

# Extra nodes for zeroLength
# node tag x y z
node 1066 0 5500 8100
node 1067 0 8800 8100

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 614 0.0 -0.0 1.0
element elasticBeamColumn 614 1066 1067 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 614

# zero_length_elements zeroLength
element zeroLength 1263 146 1066 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1264 1067 1065 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# beam_column_elements forceBeamColumn


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 96), with Mesh Node = 102 (auxiliary for element 615)
node 1068 0 14500 11600
rigidLink beam 102 1068


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 95), with Mesh Node = 101 (auxiliary for element 615)
node 1069 0 14500 14500
rigidLink beam 101 1069
# Geometric transformation command
geomTransf PDelta 615 1.0 0.0 -0.0
element forceBeamColumn 615 1068 1069 615 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 80), with Mesh Node = 86 (auxiliary for element 616)
node 1070 0 9000 11600
rigidLink beam 86 1070


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 92), with Mesh Node = 98 (auxiliary for element 616)
node 1071 0 9000 14500
rigidLink beam 98 1071
# Geometric transformation command
geomTransf PDelta 616 1.0 0.0 -0.0
element forceBeamColumn 616 1070 1071 616 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 82), with Mesh Node = 88 (auxiliary for element 617)
node 1072 4000 0 11600
rigidLink beam 88 1072


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 113), with Mesh Node = 119 (auxiliary for element 617)
node 1073 4000 0 14500
rigidLink beam 119 1073
# Geometric transformation command
geomTransf PDelta 617 1.0 0.0 -0.0
element forceBeamColumn 617 1072 1073 617 HingeRadau 12 225.0 12 225.0 13


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 618)
node 1074 12200 14500 14700
rigidLink beam 189 1074


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 618)
node 1075 15800 14500 14700
rigidLink beam 181 1075

# Extra nodes for zeroLength
# node tag x y z
node 1076 12200 14500 14700
node 1077 15800 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 618 0.0 0.0 1.0
element elasticBeamColumn 618 1076 1077 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 618

# zero_length_elements zeroLength
element zeroLength 1265 1074 1076 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1266 1077 1075 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 71), with Mesh Node = 77 (auxiliary for element 619)
node 1078 8200 14500 14700
rigidLink beam 203 1078


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 56), with Mesh Node = 62 (auxiliary for element 619)
node 1079 11800 14500 14700
rigidLink beam 189 1079

# Extra nodes for zeroLength
# node tag x y z
node 1080 8200 14500 14700
node 1081 11800 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 619 0.0 0.0 1.0
element elasticBeamColumn 619 1080 1081 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 619

# zero_length_elements zeroLength
element zeroLength 1267 1078 1080 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1268 1081 1079 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 46), with Mesh Node = 52 (auxiliary for element 620)
node 1082 16200 14500 14700
rigidLink beam 181 1082


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 48), with Mesh Node = 54 (auxiliary for element 620)
node 1083 19800 14500 14700
rigidLink beam 183 1083

# Extra nodes for zeroLength
# node tag x y z
node 1084 16200 14500 14700
node 1085 19800 14500 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 620 0.0 0.0 1.0
element elasticBeamColumn 620 1084 1085 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 620

# zero_length_elements zeroLength
element zeroLength 1269 1082 1084 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1270 1085 1083 -mat 5 5 5 5 23 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 30), with Mesh Node = 36 (auxiliary for element 621)
node 1086 8000 8800 14700
rigidLink beam 174 1086

# Extra nodes for zeroLength
# node tag x y z
node 1087 8000 5500 14700
node 1088 8000 8800 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 621 0.0 -0.0 1.0
element elasticBeamColumn 621 1087 1088 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 621

# zero_length_elements zeroLength
element zeroLength 1271 93 1087 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1272 1088 1086 -mat 5 5 5 5 34 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 30), with Mesh Node = 36 (auxiliary for element 622)
node 1089 8000 9200 14700
rigidLink beam 174 1089


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 71), with Mesh Node = 77 (auxiliary for element 622)
node 1090 8000 14300 14700
rigidLink beam 203 1090

# Extra nodes for zeroLength
# node tag x y z
node 1091 8000 9200 14700
node 1092 8000 14300 14700

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 622 0.0 -0.0 1.0
element elasticBeamColumn 622 1091 1092 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 622

# zero_length_elements zeroLength
element zeroLength 1273 1089 1091 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1274 1092 1090 -mat 5 5 5 5 33 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 72), with Mesh Node = 78 (auxiliary for element 623)
node 1093 8200 14500 18000
rigidLink beam 204 1093


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 623)
node 1094 11800 14500 18000
rigidLink beam 184 1094

# Extra nodes for zeroLength
# node tag x y z
node 1095 8200 14500 18000
node 1096 11800 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 623 0.0 0.0 1.0
element elasticBeamColumn 623 1095 1096 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 623

# zero_length_elements zeroLength
element zeroLength 1275 1093 1095 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1276 1096 1094 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 624)
node 1097 8200 9000 18000
rigidLink beam 197 1097


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 32), with Mesh Node = 38 (auxiliary for element 624)
node 1098 11800 9000 18000
rigidLink beam 176 1098

# Extra nodes for zeroLength
# node tag x y z
node 1099 8200 9000 18000
node 1100 11800 9000 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 624 0.0 0.0 1.0
element elasticBeamColumn 624 1099 1100 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 624

# zero_length_elements zeroLength
element zeroLength 1277 1097 1099 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1278 1100 1098 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 625)
node 1101 8000 5700 18000
rigidLink beam 238 1101


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 625)
node 1102 8000 8800 18000
rigidLink beam 197 1102

# Extra nodes for zeroLength
# node tag x y z
node 1103 8000 5700 18000
node 1104 8000 8800 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 625 0.0 -0.0 1.0
element elasticBeamColumn 625 1103 1104 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 625

# zero_length_elements zeroLength
element zeroLength 1279 1101 1103 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1280 1104 1102 -mat 5 5 5 5 26 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 64), with Mesh Node = 70 (auxiliary for element 626)
node 1105 8000 9200 18000
rigidLink beam 197 1105


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 72), with Mesh Node = 78 (auxiliary for element 626)
node 1106 8000 14300 18000
rigidLink beam 204 1106

# Extra nodes for zeroLength
# node tag x y z
node 1107 8000 9200 18000
node 1108 8000 14300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 626 0.0 -0.0 1.0
element elasticBeamColumn 626 1107 1108 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 626

# zero_length_elements zeroLength
element zeroLength 1281 1105 1107 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1282 1108 1106 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 627)
node 1109 4200 0 18000
rigidLink beam 247 1109


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 69), with Mesh Node = 75 (auxiliary for element 627)
node 1110 7800 0 18000
rigidLink beam 202 1110

# Extra nodes for zeroLength
# node tag x y z
node 1111 4200 0 18000
node 1112 7800 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 627 0.0 0.0 1.0
element elasticBeamColumn 627 1111 1112 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 627

# zero_length_elements zeroLength
element zeroLength 1283 1109 1111 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1284 1112 1110 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 628)
node 1113 4200 5500 18000
rigidLink beam 242 1113


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 109), with Mesh Node = 115 (auxiliary for element 628)
node 1114 7800 5500 18000
rigidLink beam 238 1114

# Extra nodes for zeroLength
# node tag x y z
node 1115 4200 5500 18000
node 1116 7800 5500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 628 0.0 0.0 1.0
element elasticBeamColumn 628 1115 1116 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 628

# zero_length_elements zeroLength
element zeroLength 1285 1113 1115 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1286 1116 1114 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 104), with Mesh Node = 110 (auxiliary for element 629)
node 1117 200 0 18000
rigidLink beam 234 1117


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 629)
node 1118 3800 0 18000
rigidLink beam 247 1118

# Extra nodes for zeroLength
# node tag x y z
node 1119 200 0 18000
node 1120 3800 0 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 629 0.0 0.0 1.0
element elasticBeamColumn 629 1119 1120 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 629

# zero_length_elements zeroLength
element zeroLength 1287 1117 1119 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1288 1120 1118 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 49), with Mesh Node = 55 (auxiliary for element 630)
node 1121 12200 14500 18000
rigidLink beam 184 1121


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 54), with Mesh Node = 60 (auxiliary for element 630)
node 1122 15800 14500 18000
rigidLink beam 187 1122

# Extra nodes for zeroLength
# node tag x y z
node 1123 12200 14500 18000
node 1124 15800 14500 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 630 0.0 0.0 1.0
element elasticBeamColumn 630 1123 1124 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 630

# zero_length_elements zeroLength
element zeroLength 1289 1121 1123 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0
element zeroLength 1290 1124 1122 -mat 5 5 5 5 24 5 -dir 1 2 3 4 5 6 -orient 1.0 0.0 0.0 0.0 1.0 0.0


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 119), with Mesh Node = 125 (auxiliary for element 631)
node 1125 4000 200 18000
rigidLink beam 247 1125


# RCJointModel3D at Geometry = 1135 (Sub-Vertex = 114), with Mesh Node = 120 (auxiliary for element 631)
node 1126 4000 5300 18000
rigidLink beam 242 1126

# Extra nodes for zeroLength
# node tag x y z
node 1127 4000 200 18000
node 1128 4000 5300 18000

# beam_column_elements elasticBeamColumn
# Geometric transformation command
geomTransf Linear 631 0.0 -0.0 1.0
element elasticBeamColumn 631 1127 1128 120000.0 25000.0 15000.0 1943850585.9374998 560000000.0 315000000.0 631

# zero_length_elements zeroLength
element zeroLength 1291 1125 1127 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0
element zeroLength 1292 1128 1126 -mat 5 5 5 5 25 5 -dir 1 2 3 4 5 6 -orient 0.0 1.0 0.0 -1.0 0.0 0.0

# truss_elements truss
element truss 632 117 63 1.0 85
element truss 633 63 58 1.0 85
element truss 634 117 65 1.0 82
element truss 635 91 124 1.0 76
element truss 636 146 111 1.0 76
element truss 637 109 108 1.0 76
element truss 638 90 146 1.0 76
element truss 639 122 91 1.0 76
element truss 640 106 96 1.0 76
element truss 641 109 130 1.0 72
element truss 642 122 109 1.0 79
element truss 643 109 124 1.0 79
element truss 644 146 96 1.0 79
element truss 645 86 146 1.0 79
element truss 646 116 97 1.0 85
element truss 647 98 122 1.0 79
element truss 648 104 86 1.0 79
element truss 649 116 88 1.0 82
element truss 650 81 147 1.0 82
element truss 651 79 80 1.0 82
element truss 652 119 145 1.0 82
element truss 653 80 100 1.0 82
element truss 654 88 123 1.0 82
element truss 655 145 89 1.0 82
element truss 656 97 105 1.0 82
element truss 657 147 97 1.0 82
element truss 658 89 131 1.0 82
element truss 659 100 92 1.0 82
element truss 660 92 107 1.0 82
element truss 661 105 130 1.0 82
element truss 662 123 85 1.0 82
element truss 663 123 97 1.0 85
element truss 664 145 80 1.0 85
element truss 665 145 92 1.0 85
element truss 666 131 92 1.0 85
element truss 667 123 130 1.0 85
element truss 668 121 98 1.0 79
element truss 669 120 80 1.0 85
element truss 670 149 104 1.0 79
element truss 671 94 83 1.0 70
element truss 672 148 88 1.0 70
element truss 673 90 119 1.0 70
element truss 674 149 80 1.0 72
element truss 675 81 98 1.0 72
element truss 676 78 147 1.0 70
element truss 677 79 101 1.0 70
element truss 678 147 99 1.0 70
element truss 679 97 109 1.0 72
element truss 680 97 95 1.0 72
element truss 681 95 130 1.0 72
element truss 682 149 101 1.0 76
element truss 683 103 147 1.0 70
element truss 684 147 102 1.0 70
element truss 685 103 105 1.0 70
element truss 686 148 122 1.0 76
element truss 687 121 148 1.0 76
element truss 688 125 116 1.0 82
element truss 689 120 119 1.0 82
element truss 690 148 125 1.0 70
