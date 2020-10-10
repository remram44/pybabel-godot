import re


__version__ = '1.0'


_godot_node = re.compile(r'^\[node name="([^"]+)" (?:type="([^"]+)")?')
_godot_property_str = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*([\[|"].+)$')
_godot_escaped_tr = re.compile(r'^.*[^A-Za-z0-9_]tr\(\\"([^\\"]+)\\"\)?')


def _godot_unquote(string):
    if string[0] != '"' or string[-1] != '"':
        return None
    result = []
    escaped = False
    for c in string[1:-1]:
        if escaped:
            if c == '\\':
                result.append('\\')
            elif c == 'n':
                result.append('\n')
            elif c == 't':
                result.append('\t')
            else:
                result.append(c)
        else:
            if c == '\\':
                escaped = True
            else:
                result.append(c)
    return ''.join(result)

def _assemble_multiline_string(line, multiline):
    to_yield = []

    if '", "' in line:
        # Multiline string ends within an array of strings
        line_parts = line.split('", "')
        multiline['value'] += line_parts[0]

        value = _godot_unquote('"' + multiline['value'] + '"')
        if value is not None:
            to_yield.append([multiline['keyword'], value])

        # Take care of intermediate strings in array (not multiline)
        for line_part in line_parts[1:-1]:
            value = _godot_unquote('"' + line_part + '"')
            if value is not None:
                to_yield.append([multiline['keyword'], value])

        # Continue with the last array item normally
        multiline['value'] = ''
        line = line_parts[-1]

    if not line.endswith('"\n') and not line.endswith(']\n'):
        # Continuation of multiline string
        multiline['value'] += line
    else:
        # Multiline string ends
        multiline['value'] += line.strip('"]\n')

        value = _godot_unquote('"' + multiline['value'] + '"')
        if value is not None:
            to_yield.append([multiline['keyword'], value])

        multiline['keyword'] = ''
        multiline['value'] = ''

    return to_yield

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

    multiline = {'keyword': '', 'value': ''}

    look_for_builtin_tr = 'tr' in keywords

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

    for lineno, line in enumerate(fileobj, start=1):
        line = line.decode(encoding)

        # Handle multiline strings
        if multiline['keyword']:
            to_yield = _assemble_multiline_string(line, multiline)
            for item in to_yield:
                yield (lineno, item[0], [item[1]], [])

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
                    # Beginning of multiline string
                    if not value.endswith('"') and not value.endswith(']'):
                        multiline['keyword'] = keyword
                        multiline['value'] = value.strip('[ "') + '\n'
                        continue

                    # Handle array of strings
                    if value.startswith('[ "'):
                        values = value.strip('[ "]').split('", "')
                        for value in values:
                            value = _godot_unquote('"' + value + '"')
                            if value is not None:
                                yield (lineno, keyword, [value], [])
                    else:
                        value = _godot_unquote(value)
                        if value is not None:
                            yield (lineno, keyword, [value], [])
        elif look_for_builtin_tr:
            # Handle Godot's tr() for built-in scripts
            match = _godot_escaped_tr.match(line)
            if match:
                value = _godot_unquote('"' + match.group(1) + '"')
                if value is not None:
                    yield (lineno, keyword, [value], [])

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

    multiline = {'keyword': '', 'value': ''}

    properties_to_translate = {}
    for keyword in keywords:
        if '/' in keyword:
            properties_to_translate[tuple(keyword.split('/', 1))] = keyword
        else:
            properties_to_translate[(None, keyword)] = keyword

    properties_to_translate = {}
    for keyword in keywords:
        if keyword.startswith('Resource/'):
            properties_to_translate[keyword[9:]] = keyword
        else:
            # Without this else-case, any '<name>' properties (not starting with 'Resource/') would be ignored
            properties_to_translate[keyword] = keyword

    def check_translate_property(property):
        return properties_to_translate.get(property)

    for lineno, line in enumerate(fileobj, start=1):
        line = line.decode(encoding)
        if line.startswith('['):
            continue

        # Handle multiline strings
        if multiline['keyword']:
            to_yield = _assemble_multiline_string(line, multiline)
            for item in to_yield:
                yield (lineno, item[0], [item[1]], [])

            continue

        match = _godot_property_str.match(line)
        if match:
            property = match.group(1)
            value = match.group(2)
            keyword = check_translate_property(property)
            if keyword:
                # Beginning of multiline string
                if not value.endswith('"') and not value.endswith(']'):
                    multiline['keyword'] = keyword
                    multiline['value'] = value.strip('[ "') + '\n'
                    continue

                # Handle array of strings
                if value.startswith('[ "'):
                    values = value.strip('[ "]').split('", "')
                    for value in values:
                        value = _godot_unquote('"' + value + '"')
                        if value is not None:
                            yield (lineno, keyword, [value], [])
                else:
                    value = _godot_unquote(value)
                    if value is not None:
                        yield (lineno, keyword, [value], [])
