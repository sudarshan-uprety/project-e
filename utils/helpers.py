def pydantic_error(err):
    if hasattr(err, 'errors'):
        errors = err.errors()
    else:
        errors = err
    msg: dict = dict()
    for error in errors:
        loc = error["loc"]
        field = loc[-1] if len(loc) > 1 else loc[0]

        error_type = error.get("type", "").split(".")[-1]
        error_msg = error.get("msg", "")

        if error_type == "missing":
            msg[field] = f"{field.capitalize()} is required."
        elif error_type == "bool":
            msg[field] = f"{field.capitalize()} is not a valid value."
        elif error_type == "enum":
            msg[field] = f"{field.capitalize()} is not a permitted value."
        elif error_type == "datetime":
            msg[field] = f"{field.capitalize()} is not a valid datetime format."
        elif error_type in ["min_length", "max_length"]:
            limit_value = error.get("ctx", {}).get("limit_value", "")
            msg[
                field] = f"{field.capitalize()} must have length {'greater' if error_type == 'min_length' else 'less'} than {limit_value}."
        elif error_type == "list":
            msg[field] = f"{field.capitalize()} is not a permitted value."
        elif error_type in ["not_gt", "not_lt"]:
            limit_value = error.get("ctx", {}).get("limit_value", "")
            msg[
                field] = f"{field.capitalize()} must be {'greater' if error_type == 'not_gt' else 'less'} than {limit_value}."
        elif error_type == "email":
            msg[field] = f"{field.capitalize()} is not a valid email address."
        elif error_type == "regex":
            msg[field] = f"{field.capitalize()} takes alphanumeric characters and symbols like ( ) / -."
        elif error_type == "integer":
            msg[field] = f"{field.capitalize()} is not a valid number."
        else:
            msg[field] = f"{field.capitalize()} {error_msg}."

    return {"body": msg}
