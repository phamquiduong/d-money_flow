import re
from typing import Annotated

from pydantic import AfterValidator, Field

import messages
from constants.regex import USERNAME_REGEX


def validate_username(username: str) -> str:
    if not re.match(USERNAME_REGEX, username):
        raise ValueError(messages.username_regex_error)
    return username


UsernameField = Annotated[str, AfterValidator(validate_username), Field(min_length=4, max_length=32)]
