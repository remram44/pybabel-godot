import re


__version__ = '1.0'


_godot_node = re.compile(r'^\[node name="([^"]+)" (?:type="([^"]+)")?')
_godot_property_str = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*(".+)\Z', re.DOTALL)


def _godot_unquote(string):
    result = []
    escaped = False
    for i, c in enumerate(string):
        if escaped:
            if c == '\\':
                result.append('\\')
            elif c == 'n':
                result.append('\n')
            elif c == 't':
                result.append('\t')
            else:
                result.append(c)
            escaped = False
        else:
            if c == '\\':
                escaped = True
            elif c == '"':
                return ''.join(result), string[i + 1:]
            else:
                result.append(c)
    return ''.join(result), None


def extract_godot_scene(fileobj, keywords, comment_tags, options):
    """Extract messages from Godot scene files (.tscn).

    :param fileobj: the seekable, file-like object the messages should be
                    extracted from
    :param keywords: a list of property names that should be localized, in the
                     format '<NodeType>/<name>' or '<name>' (example:
                     'Label/text')
    :param comment_tags: a list of translator tags to search for and include
                         in the results (ignored)
    :param options: a dictionary of additional options (optional)
    :rtype: iterator
    """
    encoding = options.get('encoding', 'utf-8')

    current_node_type = None

    properties_to_translate = {}
    for keyword in keywords:
        if '/' in keyword:
            properties_to_translate[tuple(keyword.split('/', 1))] = keyword
        else:
            properties_to_translate[(None, keyword)] = keyword

    def check_translate_property(property):
        keyword = properties_to_translate.get((current_node_type, property))
        if keyword is None:
            keyword = properties_to_translate.get((None, property))
        return keyword

    current_string = current_string_lineno = keyword = None

    for lineno, line in enumerate(fileobj, start=1):
        line = line.decode(encoding)

        if current_string:
            value, remainder = _godot_unquote(line)
            current_string.append(value)
            if remainder is None:  # Still un-terminated
                pass
            elif remainder.strip():
                raise ValueError("Trailing data after string")
            else:
                yield (
                    current_string_lineno,
                    keyword,
                    [''.join(current_string)],
                    [],
                )
                current_string = current_string_lineno = None
            continue

        match = _godot_node.match(line)
        if match:
            # Store which kind of node we're in
            current_node_type = match.group(2)
            #instanced packed scenes don't have the type field,
            #change current_node_type to empty string
            current_node_type = current_node_type \
                    if current_node_type is not None else ""
        elif line.startswith('['):
            # We're no longer in a node
            current_node_type = None
        elif current_node_type is not None:
            # Currently in a node, check properties
            match = _godot_property_str.match(line)
            if match:
                property = match.group(1)
                value = match.group(2)
                keyword = check_translate_property(property)
                if keyword:
                    value, remainder = _godot_unquote(value[1:])
                    if remainder is None:  # Un-terminated string
                        current_string = [value]
                        current_string_lineno = lineno
                    elif not remainder.strip():
                        yield (lineno, keyword, [value], [])
                    else:
                        raise ValueError("Trailing data after string")


def extract_godot_resource(fileobj, keywords, comment_tags, options):
    """Extract messages from Godot resource files (.res, .tres).

    :param fileobj: the seekable, file-like object the messages should be
                    extracted from
    :param keywords: a list of property names that should be localized, in the
                     format 'Resource/<name>' or '<name>' (example:
                     'Resource/text')
    :param comment_tags: a list of translator tags to search for and include
                         in the results (ignored)
    :param options: a dictionary of additional options (optional)
    :rtype: iterator
    """
    encoding = options.get('encoding', 'utf-8')

    properties_to_translate = {}
    for keyword in keywords:
        if keyword.startswith('Resource/'):
            properties_to_translate[keyword[9:]] = keyword

    def check_translate_property(property):
        return properties_to_translate.get(property)

    current_string = current_string_lineno = keyword = None

    for lineno, line in enumerate(fileobj, start=1):
        line = line.decode(encoding)

        if current_string:
            value, remainder = _godot_unquote(line)
            current_string.append(value)
            if remainder is None:  # Still un-terminated
                pass
            elif remainder.strip():
                raise ValueError("Trailing data after string")
            else:
                yield (
                    current_string_lineno,
                    keyword,
                    ['\n'.join(current_string)],
                    [],
                )
                current_string = current_string_lineno = None
            continue

        if line.startswith('['):
            continue

        match = _godot_property_str.match(line)
        if match:
            property = match.group(1)
            value = match.group(2)
            keyword = check_translate_property(property)
            if keyword:
                value, remainder = _godot_unquote(value[1:])
                if remainder is None:  # Un-terminated string
                    current_string = [value]
                    current_string_lineno = lineno
                elif not remainder.strip():
                    yield (lineno, keyword, [value], [])
                else:
                    raise ValueError("Trailing data after string")
