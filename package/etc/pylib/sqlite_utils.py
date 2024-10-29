import io
import pickle
from base64 import b64decode
from sqlitedict import SqliteDict


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        """Override pickle.Unpickler.find_class() to prevent deserialization of class instances."""
        raise pickle.UnpicklingError("Class deserialization is disabled")


def restricted_loads(s):
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()

def restricted_decode(obj):
    """Overwrite sqlitedict.decode() to prevent code injection."""
    return restricted_loads(bytes(obj))

def restricted_decode_key(key):
    """Overwrite sqlitedict.decode_key() to prevent code injection."""
    return restricted_loads(b64decode(key.encode("ascii")))


class RestrictedSqliteDict(SqliteDict):
    def __init__(self, *args, **kwargs):
        super(RestrictedSqliteDict, self).__init__(*args, decode=restricted_decode, decode_key=restricted_decode_key, **kwargs)