class PermissionDenied(Exception):
    pass


class UserAlreadyExistError(Exception):
    pass


class UserNotFoundError(Exception):
    pass

class UserNotVerifiedException(Exception):
    pass
class UserAlreadyVerifiedException(Exception):
    pass


class InvalidTokenException(Exception):
    pass


class DataBaseError(Exception):
    pass

class InvalidCredentials(Exception):
    pass