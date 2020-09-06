import re


__version__ = '0.2'


_godot_node = re.compile(r'^\[node name="([^"]+)" (:?type="([^"]+)")?')
_godot_property_str = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*(".+)$')
_csharp_string = re.compile(r'TranslationServer\.Translate\("(.+?)(?<!\\)"')


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


def extract_godot_scene(fileobj, keywords, comment_tags, options):
    """Extract messages from Godot scene files (.tscn).

    :param fileobj: the seekable, file-like object the messages should be
                    extracted from
    :param keywords: a list of property names that should be localized, in the
                     format 'NodeType/name' or 'name' (example: 'Label/text')
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

    for lineno, line in enumerate(fileobj, start=1):
        line = line.decode(encoding)
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
                    value = _godot_unquote(value.strip())
                    if value is not None:
                        yield (lineno, keyword, [value], [])


def extract_csharp(fileobj, keywords, comment_tags, options):
    encoding = options.get('encoding', 'utf-8')
    
    for lineno, line in enumerate(fileobj, start=1):
            line = line.decode(encoding)
            strings = _csharp_string.findall(line)
            for string in strings:
                yield (lineno, '', [string], [])
