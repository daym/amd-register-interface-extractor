#!/usr/bin/env python3

from io import StringIO

def calculate_hex_instance_value(expression_string):
    class Scanner(object):
        def __init__(self, expression_string):
            self.input_stream = StringIO(expression_string)
            self.input_LL = self.input_stream.read(1)
            self.input = None
        def consume_LL(self):
            result = self.input_LL
            self.input_LL = self.input_stream.read(1)
            return result
        def consume(self):
            result = self.input
            self.input = ""
            if self.input_LL != "":
                while self.input_LL != "" and self.input_LL == " ":
                    self.consume_LL()
                if self.input_LL in "0123456789ABCDEF":
                    while self.input_LL != "" and self.input_LL in "0123456789ABCDEF_":
                        self.input = self.input + self.consume_LL()
                    if self.input_LL == "h":
                        self.consume_LL()
                    self.input = int(self.input, 16)
                elif self.input_LL == "+":
                    self.input = self.consume_LL()
            else:
                self.input = None
            return result

    scanner = Scanner(expression_string)
    scanner.consume()
    result = scanner.consume()
    if scanner.input == "+":
        scanner.consume()
        b = scanner.consume()
        result = result + b
    if scanner.input is not None:
        raise SyntaxError(expression_string)
    return result

if __name__ == "__main__":
    assert calculate_hex_instance_value("5") == 5
    assert calculate_hex_instance_value("5h + 3") == 8
    try:
        calculate_hex_instance_value("5h + 3 +")
        assert False
    except SyntaxError:
        pass
