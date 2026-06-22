#!/usr/bin/env python3


BARE_STRING_CHARACTERS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_$./:-"
)


class OpenStepParseError(ValueError):
    pass


class OpenStepString(str):
    def __new__(cls, value, quoted=False):
        result = str.__new__(cls, value)
        result.quoted = quoted
        return result


class OpenStepParser:
    def __init__(self, text):
        self.text = text
        self.index = 0
        self.token = None

    def parse(self):
        self._advance()
        value = self._parse_value()
        if self.token[0] != "EOF":
            self._error("unexpected trailing content")
        return value

    def _advance(self):
        self.token = self._next_token()

    def _parse_value(self):
        kind, value, _ = self.token
        if kind == "STRING":
            self._advance()
            return value
        if kind == "{":
            return self._parse_dictionary()
        if kind == "(":
            return self._parse_array()
        self._error("expected a string, dictionary, or array")

    def _parse_dictionary(self):
        self._expect("{")
        result = {}
        while self.token[0] != "}":
            if self.token[0] == "EOF":
                self._error("unterminated dictionary")
            key = self._expect("STRING")
            if key in result:
                self._error("duplicate dictionary key: " + key)
            self._expect("=")
            result[key] = self._parse_value()
            self._expect(";")
        self._expect("}")
        return result

    def _parse_array(self):
        self._expect("(")
        result = []
        while self.token[0] != ")":
            if self.token[0] == "EOF":
                self._error("unterminated array")
            result.append(self._parse_value())
            if self.token[0] == ",":
                self._advance()
            elif self.token[0] != ")":
                self._error("expected ',' or ')' in array")
        self._expect(")")
        return result

    def _expect(self, kind):
        if self.token[0] != kind:
            self._error("expected " + repr(kind))
        value = self.token[1]
        self._advance()
        return value

    def _next_token(self):
        self._skip_ignored()
        if self.index >= len(self.text):
            return ("EOF", "", self.index)
        start = self.index
        character = self.text[self.index]
        if character in "{}()=;,":
            self.index += 1
            return (character, character, start)
        if character == '"':
            return ("STRING", OpenStepString(self._read_quoted_string(), True), start)
        if character == "'":
            self._error("apostrophe-quoted strings are not supported")
        return ("STRING", OpenStepString(self._read_unquoted_string()), start)

    def _skip_ignored(self):
        while self.index < len(self.text):
            if self.text[self.index].isspace():
                self.index += 1
                continue
            if self.text.startswith("//", self.index):
                newline = self.text.find("\n", self.index + 2)
                self.index = len(self.text) if newline == -1 else newline + 1
                continue
            if self.text.startswith("/*", self.index):
                end = self.text.find("*/", self.index + 2)
                if end == -1:
                    self._error("unterminated block comment")
                self.index = end + 2
                continue
            break

    def _read_quoted_string(self):
        self.index += 1
        output = []
        while self.index < len(self.text):
            character = self.text[self.index]
            self.index += 1
            if character == '"':
                return "".join(output)
            if character != "\\":
                output.append(character)
                continue
            if self.index >= len(self.text):
                self._error("unterminated string escape")
            escaped = self.text[self.index]
            self.index += 1
            escapes = {
                '"': '"',
                "'": "'",
                "\\": "\\",
                "a": "\a",
                "b": "\b",
                "f": "\f",
                "n": "\n",
                "r": "\r",
                "t": "\t",
                "v": "\v",
            }
            if escaped in escapes:
                output.append(escapes[escaped])
            elif escaped in ("\n", "\r"):
                if escaped == "\r" and self.index < len(self.text) and self.text[self.index] == "\n":
                    self.index += 1
            elif escaped == "U":
                digits = self.text[self.index:self.index + 4]
                if len(digits) != 4 or any(character not in "0123456789abcdefABCDEF" for character in digits):
                    self._error("invalid Unicode escape")
                code_unit = int(digits, 16)
                self.index += 4
                if 0xD800 <= code_unit <= 0xDBFF:
                    if not self.text.startswith("\\U", self.index):
                        self._error("unpaired high Unicode surrogate")
                    low_digits = self.text[self.index + 2:self.index + 6]
                    if (len(low_digits) != 4
                            or any(character not in "0123456789abcdefABCDEF"
                                   for character in low_digits)):
                        self._error("invalid low Unicode surrogate")
                    low_surrogate = int(low_digits, 16)
                    if not 0xDC00 <= low_surrogate <= 0xDFFF:
                        self._error("invalid low Unicode surrogate")
                    code_point = (
                        0x10000
                        + ((code_unit - 0xD800) << 10)
                        + (low_surrogate - 0xDC00)
                    )
                    output.append(chr(code_point))
                    self.index += 6
                elif 0xDC00 <= code_unit <= 0xDFFF:
                    self._error("unpaired low Unicode surrogate")
                else:
                    output.append(chr(code_unit))
            elif escaped in "01234567":
                digits = escaped
                while (len(digits) < 3 and self.index < len(self.text)
                       and self.text[self.index] in "01234567"):
                    digits += self.text[self.index]
                    self.index += 1
                output.append(chr(int(digits, 8)))
            else:
                output.append(escaped)
        self._error("unterminated quoted string")

    def _read_unquoted_string(self):
        start = self.index
        while (self.index < len(self.text)
               and self.text[self.index] in BARE_STRING_CHARACTERS):
            self.index += 1
        if self.index == start:
            self._error("invalid unquoted string")
        return self.text[start:self.index]

    def _error(self, message):
        line = self.text.count("\n", 0, self.index) + 1
        column = self.index - self.text.rfind("\n", 0, self.index)
        raise OpenStepParseError(f"{message} at line {line}, column {column}")


def parse_openstep(text):
    return OpenStepParser(text).parse()
