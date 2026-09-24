import shutil
import pcbnew as pcb
from pathlib import Path

src = Path("hardware/keyboard-v2/left/keyboard.kicad_pcb")
dst = Path("hardware/routing-work/left-v2-rebuild.kicad_pcb")
shutil.copy2(src, dst)
board = pcb.LoadBoard(str(dst))
targets = {
    "/GND_LEFT",
    "/VBAT_LEFT",
    "/RGB_EN_LEFT",
    "/RGB_5V_LEFT",
    "/RGB_DATA_SHIFTED_LEFT",
    "/power/RGB_SHIFTED_LEFT",
}
for item in list(board.GetTracks()):
    if item.GetNetname() in targets:
        board.Remove(item)
pcb.SaveBoard(str(dst), board)
print("rebuilt candidate", dst)
