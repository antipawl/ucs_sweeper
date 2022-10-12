import re


def slugify(value):
    """
    Modified slugify:
    Convert spaces to hyphens, dots to underscores.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s.-]', '', value).strip().lower()
    value = re.sub(r'\.+', '_', value)
    return re.sub(r'[-\s]+', '-', value)
