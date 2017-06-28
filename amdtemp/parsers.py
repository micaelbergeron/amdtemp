import re

class IntParser:
    def __init__(self, name):
        self.name = name

    def parse(self, raw):
        return {self.name: int(raw)}


"""
Parse value using a regex an output named groups as fields.
"""
class RegexParser:
    def __init__(self, name, regex):
        self.name = name
        self.compiled = re.compile(regex, flags=re.M|re.I)

    def parse(self, raw):
        fields = dict()
        for field, value in self.compiled.search(raw).groupdict().items():
            complete_name = '.'.join((self.name, field))
            fields[complete_name] = int(value)
        return fields
