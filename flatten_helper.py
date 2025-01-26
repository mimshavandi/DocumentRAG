# flatten_helpers.py

"""
Utility functions to flatten (serialize) different field types into a textual representation
based on the "fieldType" property.
"""

def flatten_checkbox_field(field_name: str, value: bool) -> str:
    """
    Convert a checkbox field into text: 'FieldName: Checked' or 'FieldName: Unchecked'.
    """
    status = "Checked" if value else "Unchecked"
    return f"{field_name}: {status}"


def flatten_text_field(field_name: str, value: str) -> str:
    """
    Convert a text field into 'FieldName: SomeValue'.
    """
    return f"{field_name}: {value}"


def flatten_number_field(field_name: str, value) -> str:
    """
    Convert a number field into 'FieldName: 123'.
    """
    return f"{field_name}: {value}"


def flatten_password_field(field_name: str) -> str:
    """
    For a password field, do NOT store the actual password. Redact it.
    """
    return f"{field_name}: [REDACTED]"


def flatten_date_field(field_name: str, value: str) -> str:
    """
    Convert a date/time field to text. You could validate the format or just store as-is.
    Example: 'BirthDate: 2025-04-15'
    """
    return f"{field_name}: {value}"


def flatten_address_field(field_name: str, address_value: dict) -> str:
    """
    Convert an address object (with line1, line2, city, state, zip, etc.) to a single text line.

    Example address_value:
    {
      "line1": "123 Main St",
      "line2": "Apt 2",
      "city": "Springfield",
      "state": "IL",
      "zip": "12345"
    }
    """
    line1 = address_value.get("line1", "")
    line2 = address_value.get("line2", "")
    city = address_value.get("city", "")
    state = address_value.get("state", "")
    zip_code = address_value.get("zip", "")
    
    parts = [line1, line2, city, state, zip_code]
    joined = ", ".join(p for p in parts if p)
    return f"{field_name}: {joined}"


def flatten_table_field(field_name: str, rows: list) -> str:
    """
    Convert a table (list of row objects) into a multiline string.
    Example rows:
      [
        {"Item": "Paper Clips", "Quantity": 3},
        {"Item": "Markers", "Quantity": 5}
      ]
    Returns something like:
      "OrderItems:
         Row1: [Item=Paper Clips, Quantity=3]
         Row2: [Item=Markers, Quantity=5]"
    """
    lines = [f"{field_name}:"]
    for i, row in enumerate(rows, start=1):
        row_content = ", ".join(f"{k}={v}" for k, v in row.items())
        lines.append(f"  Row{i}: [{row_content}]")
    return "\n".join(lines)


def flatten_signature_field(field_name: str, value: dict) -> str:
    """
    For a signature field, store a placeholder or minimal info.
    E.g. 'Signature: provided on 2025-04-15T10:00:00Z'
    If you have a timestamp or file reference, include it. Otherwise, just say '[Signature provided]'.

    Example value:
    {
      "timestamp": "2025-04-15T10:00:00Z",
      "fileRef": "sig_abc.png"
    }
    """
    ts = value.get("timestamp", "")
    file_ref = value.get("fileRef", "")
    text = f"{field_name}: Signature provided"
    if ts:
        text += f" at {ts}"
    if file_ref:
        text += f", file: {file_ref}"
    return text


def flatten_location_field(field_name: str, value: dict) -> str:
    """
    If you have a location object, e.g. { "lat": 35.6895, "lon": 139.6917 }
    or an address string. Customize as needed.
    """
    lat = value.get("lat")
    lon = value.get("lon")
    if lat is not None and lon is not None:
        return f"{field_name}: (Lat={lat}, Lon={lon})"
    return f"{field_name}: [Location data]"  # fallback


def flatten_field(field_data: dict) -> str:
    """
    Given a single field dictionary with keys:
      "fieldType", "fieldName", and "value"
    decide which flatten_* function to call.

    Returns a single-line or multi-line string describing that field.
    """
    field_type = field_data.get("fieldType")
    field_name = field_data.get("fieldName", "UnknownField")
    value = field_data.get("value")

    if field_type == "checkbox":
        # value should be boolean
        return flatten_checkbox_field(field_name, bool(value))
    
    elif field_type == "text":
        # value should be a string
        # fallback if it's not
        return flatten_text_field(field_name, str(value))
    
    elif field_type == "number":
        return flatten_number_field(field_name, value)

    elif field_type == "password":
        return flatten_password_field(field_name)
    
    elif field_type == "date":
        return flatten_date_field(field_name, str(value))
    
    elif field_type == "address":
        # assume value is a dict with line1, line2, city, etc.
        if isinstance(value, dict):
            return flatten_address_field(field_name, value)
        else:
            # fallback
            return f"{field_name}: [Invalid address data]"
    
    elif field_type == "table":
        # assume value is a list of row objects
        if isinstance(value, list):
            return flatten_table_field(field_name, value)
        else:
            return f"{field_name}: [Invalid table data]"
    
    elif field_type == "signature":
        # assume value is a dict with signature metadata
        if isinstance(value, dict):
            return flatten_signature_field(field_name, value)
        else:
            return f"{field_name}: [Signature provided]"
    
    elif field_type == "location":
        # assume value is a dict with lat/lon
        if isinstance(value, dict):
            return flatten_location_field(field_name, value)
        else:
            return f"{field_name}: [Location data]"
    
    else:
        # default fallback for unknown types
        return f"{field_name}: {value}"


def flatten_submission(submission_doc: dict) -> str:
    """
    High-level function to flatten an entire submission into a text block.

    Example submission_doc structure:
    {
      "_id": "result123",
      "user_id": "userXYZ",
      "folder_id": "folderABC",
      "document_id": "doc789",
      "timestamp": "2025-04-15T10:00:00Z",
      "fieldValues": [
        {
          "fieldType": "text",
          "fieldName": "FirstName",
          "value": "Alice"
        },
        {
          "fieldType": "checkbox",
          "fieldName": "NewsletterOpt",
          "value": true
        },
        ...
      ]
    }

    Returns a multiline string summarizing the submission.
    """
    lines = []
    
    # Basic submission info
    submission_id = submission_doc.get("_id", "")
    folder_id = submission_doc.get("folder_id", "")
    document_id = submission_doc.get("document_id", "")
    user_id = submission_doc.get("user_id", "")
    timestamp = submission_doc.get("timestamp", "")
    
    lines.append(f"Submission (Result ID: {submission_id})")
    lines.append(f"For Document: {document_id} in Folder: {folder_id}.")
    lines.append(f"Owned by user: {user_id}.")
    lines.append(f"Timestamp: {timestamp}.")
    
    field_values = submission_doc.get("fieldValues", [])
    lines.append("Field Values:")
    
    # Loop through each field entry, flatten based on the fieldType
    for field_entry in field_values:
        flattened_text = flatten_field(field_entry)
        # Indent for readability
        lines.append("  " + flattened_text)
    
    # Join everything into a single multiline string
    return "\n".join(lines)
