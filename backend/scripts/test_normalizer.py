from normalizer import normalize_medicine

tests = [
    '"Hyperox" Peracetic Acid + Hydrogen Peroxide liquid',
    'Aceclofenac SR Tablets 100 mg',
    'Aceclofenac Roll-On',
    'Aceclofenac W/W + Menthol Spray',
    'Abacavir sulphate oral',
    ': [C]',
    ': In',
    '. Probio : Sachet Contains',
    'Wheelchair',
]

for t in tests:
    print("=" * 60)
    print("INPUT :", t)
    print("OUTPUT:", normalize_medicine(t))