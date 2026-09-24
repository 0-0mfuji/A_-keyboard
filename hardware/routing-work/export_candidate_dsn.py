import pcbnew
from pathlib import Path

board_path = Path("hardware/routing-work/left-v2-rebuild.kicad_pcb")
dsn_path = Path("hardware/routing-work/left-v2-rebuild.dsn")
board = pcbnew.LoadBoard(str(board_path))
if not pcbnew.ExportSpecctraDSN(board, str(dsn_path)):
    raise SystemExit("Specctra export failed")
print(dsn_path)
