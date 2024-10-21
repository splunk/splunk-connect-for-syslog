import builtins
import io
import pickle
from base64 import b64decode
from sqlitedict import SqliteDict

safe_builtins = {
    'range',
    'complex',
    'set',
    'frozenset',
    'slice',
}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Only allow safe classes from builtins.
        if module == "builtins" and name in safe_builtins:
            return getattr(builtins, name)
        # Forbid everything else.
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (module, name))

def restricted_loads(s):
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()

def restricted_decode(obj):
    """Overwrite sqlitedict.decode to prevent code injection."""
    return restricted_loads(bytes(obj))

def restricted_decode_key(key):
    """Overwrite sqlitedict.decode_key to prevent code injection."""
    return restricted_loads(b64decode(key.encode("ascii")))


class RestrictedSqliteDict(SqliteDict):
    def __init__(self, *args, **kwargs):
        super(RestrictedSqliteDict, self).__init__(*args, decode=restricted_decode, decode_key=restricted_decode_key, **kwargs)