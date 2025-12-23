class PlaylistResolutionError(RuntimeError):
    pass


class PreconditionFailure(RuntimeError):
    def __init__(self, message: str, *, stage: str | None = None) -> None:
        super().__init__(message)
        self.stage = stage
