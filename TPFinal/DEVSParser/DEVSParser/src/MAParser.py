import string

import pyparsing as pp
from enum import Enum


class MAParserError(Exception):
    def __init__(self, msg="MAParser error"):
        self.msg = msg
        super().__init__(msg)


class MAParser:
    def __init__(self):
        keyword_begin_model_name = pp.Literal('[')
        keyword_end_model_name = pp.Literal(']')
        keyword_assign_attribute = pp.Keyword(':')
        keyword_comment = pp.Keyword('%')
        keyword_model_instance = pp.Literal('@')
        keyword_link_at = keyword_model_instance
        keyword_components = pp.CaselessKeyword("components")
        keyword_in = pp.CaselessKeyword("in")
        keyword_out = pp.CaselessKeyword("out")
        keyword_link = pp.CaselessKeyword("link")

        value_component_atomic = pp.Word(pp.printables)
        value_component_complex = pp.Word(pp.alphas)
        value_component = pp.MatchFirst(value_component_atomic, value_component_complex)
        word_components = keyword_components + keyword_assign_attribute + pp.OneOrMore(value_component)

        word_in = keyword_in + keyword_assign_attribute + pp.OneOrMore(pp.Word(pp.printables))
        word_out = keyword_out + keyword_assign_attribute + pp.OneOrMore(pp.Word(pp.printables))

        value_link_own = pp.Word(pp.printables)
        value_link_other = pp.Word(pp.printables) + keyword_link_at + pp.Word(pp.printables)
        value_link = pp.Or(value_link_own, value_link_other)
        word_link = keyword_link + keyword_assign_attribute + pp.OneOrMore(value_link)

        word_user_attribute = pp.Word(pp.printables) + keyword_assign_attribute + pp.OneOrMore(pp.Word(pp.printables))
        word_attribute = word_components("COMPONENTS") ^ word_in("IN") ^ word_out("OUT") ^ word_link("LINK") ^\
                         word_user_attribute("ATTR")

        word_header = keyword_begin_model_name + pp.Word(pp.alphas) + keyword_end_model_name
        word_comment = keyword_comment + pp.ZeroOrMore(pp.Word(pp.printables))

        self.parser = word_comment("COMMENT") ^ word_header("DEFINITION") ^ word_attribute("ATTRIBUTE")

    def parse_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(self.scan_line(line))

    def scan_text(self, text):
        res = []
        lines = text.splitlines()
        for line in lines:
            res.append(self.scan_line(line))
        return res

    def scan_line(self, line):
        try:
            return self.parser.parseString(line)
        except pp.ParseException as e:
            print(e.line)
            raise MAParserError
