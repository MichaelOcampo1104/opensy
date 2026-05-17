import openseespy.opensees as ops
ops.wipe()
ops.model('BasicBuilder', '-ndm', 2, '-ndf', 3)
ops.node(1, 0.0, 0.0)
ops.node(2, 0.0, 0.0)
ops.uniaxialMaterial('Elastic', 1, 1000.0)
try:
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 1, '-orient', 0, -1, 0, 1, 0, 0)
    print("6 values worked!")
except Exception as e:
    print(f"6 values failed: {e}")

try:
    ops.element('zeroLength', 2, 1, 2, '-mat', 1, '-dir', 1, '-orient', 0, -1, 1, 0)
    print("4 values worked!")
except Exception as e:
    print(f"4 values failed: {e}")
