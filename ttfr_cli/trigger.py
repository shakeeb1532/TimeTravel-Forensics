import os
from datetime import datetime
from .engine import get_engine
from .utils import info, success

SNAP_DIR = "snapshots"
os.makedirs(SNAP_DIR, exist_ok=True)

def flush(reason="manual"):
    engine = get_engine()

    info(f"Trigger received: {reason}")
    data = engine.dump_snapshot()

    fname = f"snapshot_{reason}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ttfr"
    path = os.path.join(SNAP_DIR, fname)

    with open(path, "wb") as f:
        f.write(data)

    success(f"Snapshot saved → {path}")
    return path

