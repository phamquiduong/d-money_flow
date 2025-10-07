from fastapi import HTTPException


class APIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        fields: dict[str, str | list[str]] | None = None
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.fields = {
            field: error if isinstance(error, list) else [error]
            for field, error in fields.items()
        } if fields else {}

    def __str__(self) -> str:
        return self.detail
