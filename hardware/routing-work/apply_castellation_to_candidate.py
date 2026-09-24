import pcbnew, shutil, sys

src, out = sys.argv[1:]
shutil.copy2(src, out)
b = pcbnew.LoadBoard(out)
mm = pcbnew.FromMM
v = pcbnew.VECTOR2I
spec = {
    '17': (1.80, 1.20, 0.45),
    '27': (1.80, 1.40, 0.45),
    '28': (2.50, 1.10, 0.50),
    '29': (2.50, 1.10, 0.50),
}
for ref in ('U1', 'U2'):
    fp = next((x for x in b.GetFootprints() if x.GetReference() == ref), None)
    if fp is None:
        continue
    for pad in fp.Pads():
        if pad.GetNumber() not in spec:
            continue
        sx, sy, drill = spec[pad.GetNumber()]
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetShape(pcbnew.PAD_SHAPE_OVAL)
        pad.SetSize(v(mm(sx), mm(sy)))
        pad.SetDrillSize(v(mm(drill), mm(drill)))
b.Save(out)
print(out)
