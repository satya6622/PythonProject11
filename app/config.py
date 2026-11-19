from pathlib import Path
import os

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{Path('subledger.db').absolute()}")
