import re

_compile_error_regex = re.compile(r'.*:[0-9]+:[0-9]+: (fatal error|error).*')
_reference_error_regex = re.compile(r'.*:[0-9]+: .*')


def _is_error(line, regex):
    return line != "" and not line.startswith("scons") and regex.match(line) is not None


def _construct_error(error_str, fine_path, line, column=0):
    error_str = error_str.decode('string_escape').strip()
    return dict(file=fine_path, line=int(line), column=int(column), error=error_str)


def _parse_compile_error(line):
    split_line = line.split(":", 4)
    return _construct_error(split_line[4], split_line[0], split_line[1], split_line[2])


def _parse_reference_error(line):
    split_line = line.split(":", 3)
    return _construct_error(split_line[2], split_line[0], split_line[1])


def _get_errors(error_str):
    errors = []
    lines = error_str.split("\n\n", 1)[-1].split("\n")
    for line in lines:
        if _is_error(line, _compile_error_regex):
            errors.append(_parse_compile_error(line))
        elif _is_error(line, _reference_error_regex):
            errors.append(_parse_reference_error(line))
    return errors


def format_compile_result(result):
    if result[0]:
        return result
    error_str = result[1]["err"]
    errors = _get_errors(error_str)
    if len(errors) > 0:
        result[1]["err"] = errors
    return result
