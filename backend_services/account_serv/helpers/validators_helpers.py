def is_email(value: str) -> bool:
    value_split = value.split("@")

    return "@" in value and len(value_split) == 2


def is_phone_number(value: str) -> bool:
    return value.startswith("+") and "@" not in value and value[1:].isdigit()

def is_valid_serializer( serializer):
    return serializer.is_valid(raise_exception=True)