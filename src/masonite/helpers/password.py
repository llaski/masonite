"""Password Helper Module."""

import bcrypt


def password(password_string):
    """Bcrypt a string.

    Useful for storing passwords in a database.

    Arguments:
        pass {string} -- A string like a users plain text password to be bcrypted.

    Returns:
        string -- The encrypted string.
    """
    return bytes(bcrypt.hashpw(
        bytes(password_string, 'utf-8'), bcrypt.gensalt()
    )).decode('utf-8')
