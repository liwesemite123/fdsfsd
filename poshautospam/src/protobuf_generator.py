def write_varint(value: int) -> bytes:
    result = bytearray()
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)


def write_string_field(field_number: int, value: str) -> bytes:
    key = (field_number << 3) | 2
    value_bytes = value.encode("utf-8")
    return bytes([key]) + write_varint(len(value_bytes)) + value_bytes


def write_bytes_field(field_number: int, value: bytes) -> bytes:
    key = (field_number << 3) | 2
    return bytes([key]) + write_varint(len(value)) + value


def write_varint_field(field_number: int, value: int) -> bytes:
    key = (field_number << 3) | 0
    return bytes([key]) + write_varint(value)


def build_create_project_payload(
    unit_token: str,
    project_name: str,
    contact_tokens: list[str],
    timezone: str = "Europe/London"
) -> bytes:

    inner = bytearray()
    inner.extend(write_string_field(3, unit_token))
    inner.extend(write_string_field(6, project_name))

    for idx, contact_token in enumerate(contact_tokens):
        contact_msg = bytearray()
        contact_msg.extend(write_string_field(1, contact_token))
        if idx == 0:
            contact_msg.extend(write_varint_field(5, 1))

        inner.extend(write_bytes_field(11, bytes(contact_msg)))

    inner.extend(write_string_field(15, ""))

    inner.append(0xBA)
    inner.append(0x01)
    inner.append(0x0D)
    inner.extend(timezone.encode("utf-8"))

    return write_bytes_field(1, bytes(inner))
