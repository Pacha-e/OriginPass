"""Signing and chaining, the two things that make a record hard to rewrite.

A hash computed only from the columns it protects is worth very little: anyone
who can write to those columns can recompute it and leave the row looking
untouched. Every value here is signed with a key held by the application and
never stored in the database, so an attacker holding only the database cannot
produce a matching signature.

Chaining does the other half. Each record carries the signature of the record
before it, so rewriting one row invalidates every row after it, and removing a
row leaves a gap that does not join up.

## What this does and does not give you

It makes tampering **detectable by anyone holding the key**. It does not make
tampering impossible, and it does not protect against whoever runs the server,
who holds the key as well as the database and can therefore rebuild the whole
chain consistently.

Closing that last gap needs the head of the chain published somewhere the
operator does not control — a timestamping authority, or a public ledger — so
that a rebuilt chain no longer matches what was published. That is the anchoring
step, and it is not implemented here.
"""

from django.utils.crypto import constant_time_compare, salted_hmac

#: Namespaces the derived key. Changing it invalidates every existing signature,
#: which is the point: it is how a signing scheme is versioned.
KEY_SALT = "originpass.integrity.v1"

#: Stands in for the signature of the record before the first one.
GENESIS = "0" * 64

#: Separates the parts of a signed value so that ("ab", "c") and ("a", "bc")
#: cannot produce the same signature.
SEPARATOR = "\x1f"


def sign(*parts):
    """Sign the parts with a key derived from SECRET_KEY, never stored in the database."""
    payload = SEPARATOR.join("" if part is None else str(part) for part in parts)
    return salted_hmac(KEY_SALT, payload, algorithm="sha256").hexdigest()


def matches(signature, *parts):
    """Whether `signature` is the signature of `parts`, compared in constant time."""
    return constant_time_compare(signature or "", sign(*parts))


def verify_chain(records, parts_of):
    """Walk a chain of records and return the first one that does not hold up.

    `parts_of(record)` gives the values that record's signature covers, without
    the link to the previous one, which is added here.

    Returns `(ok, problem)`. `problem` is None when the chain holds, otherwise a
    string naming the record and what is wrong with it.
    """
    previous = GENESIS

    for record in records:
        if record.previous_hash != previous:
            return False, (
                f"{record.__class__.__name__} #{record.pk} does not follow the record "
                f"before it: a record has been removed or reordered"
            )
        if not matches(record.entry_hash, record.previous_hash, *parts_of(record)):
            return False, (
                f"{record.__class__.__name__} #{record.pk} has been altered since it was written"
            )
        previous = record.entry_hash

    return True, None
