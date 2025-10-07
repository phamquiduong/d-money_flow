import re
from typing import Annotated

from pydantic import AfterValidator, Field

import messages
from constants.regex import PASSWORD_REGEX


def validate_password(password: str) -> str:
    if not re.match(PASSWORD_REGEX, password):
        raise ValueError(messages.pass_regex_err)
    return password


PasswordField = Annotated[str, AfterValidator(validate_password), Field(min_length=6, max_length=32)]
