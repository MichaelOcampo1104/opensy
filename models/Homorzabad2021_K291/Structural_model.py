# print('Start running structural model.')

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

exec(open("Structural Model/01-SetParameters.py").read())
exec(open("Structural Model/02-Nodes.py").read())
exec(open("Structural Model/03-Constraints.py").read())
exec(open("Structural Model/04-GeomTrans.py").read())
exec(open("Structural Model/05-Materials.py").read())
exec(open("Structural Model/06-Elements.py").read())
exec(open("Structural Model/07-Mass.py").read())
exec(open("Structural Model/08-Rayleigh.py").read())
exec(open("Structural Model/09-ModalAnalysis.py").read())

# Gravity analysis------------------------------------------------
exec(open("Structural Model/10-GravityLoadPatterns.py").read())
exec(open("Structural Model/11-GravityAnalysis.py").read())

# Dynamic analysis------------------------------------------------
exec(open("Structural Model/12-Recorders.py").read())
exec(open("Structural Model/13-DynamicAnalysis.py").read())

ops.wipe(); # to close OpnenSees model and update output files.