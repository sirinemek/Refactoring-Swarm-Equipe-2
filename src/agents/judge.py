from pathlib import Path
from src.utils.TheToolSmith import run_command
from typing import Tuple

class Judge:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def test(self) -> Tuple[bool, str]:
        cmd = ["pytest", str(self.base_dir)]
        returncode, stdout, stderr = run_command(cmd)
        success = returncode == 0
        logs = stdout + "\n" + stderr
        return success, logs