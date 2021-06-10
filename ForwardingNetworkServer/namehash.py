import codecs
import functools

# from sha3 import sha3_256
# from sha3 import keccak_256 as sha3_256
# import hashlib
from Crypto.Hash import keccak
import idna


def is_bytes(value):
    return isinstance(value, (bytes, bytearray))


def combine(f, g):
    return lambda x: f(g(x))


def compose(*functions):
    return functools.reduce(combine, functions, lambda x: x)


def sha3(value):
    # return hashlib.sha3_256(value).digest()
    # return sha3_256(value).digest()
    # value = value.decode("utf8")
    k = keccak.new(digest_bits=256)
    k.update(value)
    return k.digest()


# ensure we have the *correct* sha3 installed (keccak)
assert codecs.encode(sha3(b''), 'hex') == b'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'  # noqa


def _sub_hash(value, label):
    return sha3(value + sha3(label))


def normalize_name(name):
    '''
    Clean the fully qualified name, as defined in ENS `EIP-137
    <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-137.md#name-syntax>`_
    This does *not* enforce whether ``name`` is a label or fully qualified domain.
    :param str name: the dot-separated ENS name
    :raises InvalidName: if ``name`` has invalid syntax
    '''
    if not name:
        return name
    elif isinstance(name, (bytes, bytearray)):
        name = name.decode('utf-8')
    try:
        return idna.decode(name, uts46=True, std3_rules=True)
    except idna.IDNAError as exc:
        raise InvalidName("%s is an invalid name, because %s" % (name, exc)) from exc


def label_to_hash(label):
    label = normalize_name(label)
    if '.' in label:
        raise ValueError("Cannot generate hash for label %r with a '.'" % label)
    return sha3(label)


def namehash(name, encoding=None):
    """
    Implementation of the namehash algorithm from EIP137.
    """
    node = b'\x00' * 32
    if name:
        if encoding is None:
            if is_bytes(name):
                encoded_name = name
            else:
                encoded_name = codecs.encode(name, 'utf8')
        else:
            encoded_name = codecs.encode(name, encoding)

        labels = encoded_name.split(b'.')

        for label in labels :
            label = normalize_name(label)

        return "0x" + compose(*(
            functools.partial(_sub_hash, label=label)
            for label
            in labels
        ))(node).hex()
    return "0x" + node.hex()
