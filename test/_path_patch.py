# add the project directory to the pythonpath
import sys
from pathlib import Path

dir_ = Path(__file__).parent
sys.path.insert(0, str(dir_.parent))
