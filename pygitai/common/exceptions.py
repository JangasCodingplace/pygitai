class NoJobConfigured(Exception):
    """No job configured"""


class JobImproperlyConfigured(Exception):
    """Job Improperly configured"""


class InvalidRole(Exception):
    """Invalid role"""


class DoesNotExist(Exception):
    pass
