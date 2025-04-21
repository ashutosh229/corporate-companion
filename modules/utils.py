import phonenumbers


def sanitize_text(value, default="Not provided"):
    value = value.strip() if value else ""
    return value if value else default


def normalize_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, "IN")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
        else:
            return "Invalid number"
    except phonenumbers.NumberParseException:
        return "Invalid number"
