class NotSklearnModelError(Exception):
    """No sklearn model exception"""

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


class SklearnInternalError(Exception):
    """Internal sklearn exception"""

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


class NotKerasModelError(Exception):
    """No keras model exception"""

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


class KerasInternalError(Exception):
    """Internal keras exception"""

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


class ModelNotLoadedError(Exception):
    """Model is used before loaded"""

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


class UnknownModelError(Exception):
    """Unknown model exception"""

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
