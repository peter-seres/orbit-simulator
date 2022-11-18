class ImmutableError(Exception):
    pass


class Immutable(type):
    """A type whose attributes are immutable.
    Modifying the variables throws an exception.
    Use it for global consts.
    """

    def __setattr__(cls, key, value):
        raise ImmutableError(f"Class {cls} is immutable. Cannot set variables.")

    def __delattr__(cls, key):
        raise ImmutableError(f"Class {cls} is immutable. Cannot delete variables.")


class Settings(metaclass=Immutable):
    pass
