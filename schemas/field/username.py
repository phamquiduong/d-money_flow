import re
from typing import Annotated

from pydantic import AfterValidator, Field

from constants.regex import USERNAME_REGEX


def validate_username(username: str) -> str:
    if not re.match(USERNAME_REGEX, username):
        raise ValueError('Invalid username format')
    return username


UsernameField = Annotated[str, AfterValidator(validate_username), Field(min_length=4, max_length=32)]
