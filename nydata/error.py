class NyDataBaseError(Exception):
    pass


class LogRegexPatternNotFound(NyDataBaseError):
    pass


class LogTransformerNotFound(NyDataBaseError):
    pass


class InvalidUserConfiguration(NyDataBaseError):
    pass


class DbError(NyDataBaseError):
    pass


class LogLineAlreadyInDb(DbError):
    pass
