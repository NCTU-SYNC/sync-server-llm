def contains_placeholder(*placeholders: str):
    def validate_template(template: str):
        for placeholder in placeholders:
            if f"{{{placeholder}}}" not in template:
                raise ValueError(f"Template must contain '{{{placeholder}}}'")
        return template

    return validate_template
