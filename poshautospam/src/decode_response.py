import re


def parse_create_project_response(response_bytes: bytes) -> dict:
    result = {
        "project_token": None,
        "project_name": None,
        "unit_token": None,
        "contacts": [],
        "timezone": None,
        "phase_token": None
    }

    project_token_pattern = rb"(proj_[A-Z0-9]{26})(?!ph_)"
    match = re.search(project_token_pattern, response_bytes)
    if match:
        result["project_token"] = match.group(1).decode("utf-8")

    phase_token_pattern = rb"(projph_[A-Z0-9]{26})"
    match = re.search(phase_token_pattern, response_bytes)
    if match:
        result["phase_token"] = match.group(1).decode("utf-8")

    timezone_pattern = rb"(Etc/[A-Z]{3})"
    match = re.search(timezone_pattern, response_bytes)
    if match:
        result["timezone"] = match.group(1).decode("utf-8")

    email_pattern = rb"([a-zA-Z0-9._+-]+@gmail\.com)"
    emails = [email.decode("utf-8") for email in re.findall(email_pattern, response_bytes)]

    token_pattern = rb"([A-Z0-9]{26})"
    all_tokens = [token.decode("utf-8") for token in re.findall(token_pattern, response_bytes)]

    contact_tokens = []
    for token in all_tokens:
        if result["project_token"] and token in result["project_token"]:
            continue
        if result["phase_token"] and token in result["phase_token"]:
            continue
        contact_tokens.append(token)


    name_pattern = rb"[A-Z0-9]{26}\x12(.+?)\x20?\x01?\x28?\x00?\x32[a-zA-Z0-9._+-]+@gmail\.com"
    names_raw = re.findall(name_pattern, response_bytes)

    names = []
    for name_bytes in names_raw:
        try:
            if len(name_bytes) > 1:
                name_len = name_bytes[0]
                if 0 < name_len < len(name_bytes):
                    name = name_bytes[1:name_len+1].decode("utf-8", errors="ignore").strip()
                    if name:
                        names.append(name)
                else:
                    name = name_bytes.decode("utf-8", errors="ignore").strip()
                    if name and len(name) > 1:
                        names.append(name)
        except:
            pass

    num_contacts = min(len(contact_tokens), len(emails))

    for i in range(num_contacts):
        contact = {
            "token": contact_tokens[i] if i < len(contact_tokens) else None,
            "email": emails[i] if i < len(emails) else None,
            "name": names[i] if i < len(names) else None
        }
        result["contacts"].append(contact)

    project_name_pattern = rb"([A-Za-z_][A-Za-z0-9_]*\d{5,})"
    match = re.search(project_name_pattern, response_bytes)
    if match:
        result["project_name"] = match.group(1).decode("utf-8")

    unit_token_pattern = rb"([A-Z0-9]{13})\x22"
    match = re.search(unit_token_pattern, response_bytes)
    if match:
        result["unit_token"] = match.group(1).decode("utf-8")

    return result
