import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

import sqlalchemy.orm as orm

# Monkeypatch DeclarativeBase to avoid SQLAlchemy mapping during import
OriginalDeclarativeBase = getattr(orm, 'DeclarativeBase', None)
class DummyBase:
    pass
orm.DeclarativeBase = DummyBase

try:
    import importlib
    m = importlib.import_module('backend.database.models')
    for name, obj in vars(m).items():
        if isinstance(obj, type) and hasattr(obj, '__tablename__'):
            print('Class', name)
            ann = getattr(obj, '__annotations__', {})
            for k, v in ann.items():
                    print(' ', k, '->', repr(v), 'type:', type(v))
                    # inspect typing internals if possible
                    try:
                        args = getattr(v, '__args__', None)
                        if args is not None:
                            print('   args:', args)
                            for a in args:
                                print('    arg type:', type(a), 'repr:', repr(a))
                    except Exception as e:
                        print('   could not inspect args:', e)
            print()
finally:
    # restore
    if OriginalDeclarativeBase is not None:
        orm.DeclarativeBase = OriginalDeclarativeBase
