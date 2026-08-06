from importlib import import_module
import inspect
import sys
from pathlib import Path

# Ensure workspace root is on sys.path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

m = import_module('backend.database.models')
for name, obj in vars(m).items():
    if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
        print(f'Class {name}:')
        ann = getattr(obj, '__annotations__', {})
        for k, v in ann.items():
            print(' ', k, '->', repr(v), 'type:', type(v))
        print()
