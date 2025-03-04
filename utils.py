import bs4

def clean_xml_string(s: str):
    start = s.find("<")
    end = s.rfind(">")

    if start == -1 or end == -1 or start > end:
        return ""  # Return an empty string if no valid < > pair is found

    trimmed_string = s[start : end + 1]

    return trimmed_string.replace("\n", "")

def extract_xml_tag(content: str, tag: str):
    soup = bs4.BeautifulSoup(content, features="html.parser")
    match = soup.find(tag)
    return match.get_text() if match else None


def extract_xml_tags(content: str, tag: str) -> list[str]:
    soup = bs4.BeautifulSoup(content, features="html.parser")
    matches = soup.find_all(tag)
    return [match.get_text() for match in matches]


def extract_all_xml_tags_properties(
    content: str,
    tag: str,
    properties: list[str],
    attributes: list[str] | None = None,
):
    soup = bs4.BeautifulSoup(markup=content, features="html.parser")
    matches = soup.find_all(tag)
    results = list[dict[str, str | None]]()
    if set(properties) & set(attributes or []):
        raise ValueError("properties and attributes must be disjoint sets")
    for match in matches:
        result = dict[str, str | None]()
        for prop in properties:
            prop_match = match.find(prop)
            if prop_match:
                result[prop] = prop_match.get_text()
            else:
                result[prop] = None
        for attribute in attributes or []:
            result[attribute] = match.get(attribute)
        results.append(result)

    return results