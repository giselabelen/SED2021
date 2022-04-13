import pyparsing as pp
from enum import Enum, unique, auto

_MAprintables_ = pp.printables.replace(":", "")


@unique
class MATokens(Enum):
    MODEL_DEF = auto()
    MODEL_DEFINITIONS = auto()
    MODELS = auto()
    CURRENT_MODEL = auto()
    IN = auto()
    OUT = auto()
    LINK = auto()
    COMPONENTS = auto()
    ATTR = auto()
    LOCAL_PORT = auto()
    REMOTE_PORT = auto()
    ATOMIC = auto()
    COMPOSITE = auto()
    IS_ATOMIC = auto()
    COMMENT = auto()


class MAParserError(Exception):
    def __init__(self, msg="MAParser error", col=-1, nro_line=-1, line=None):
        self.msg = msg
        self.col = col
        self.nro_line = nro_line
        self.line = line
        super().__init__(msg)

    def __repr__(self):
        return self.msg, self.col, self.nro_line, self.line

    def __str__(self):
        read_so_far = ""
        if self.line:
            read_so_far = f"Content: '{self.line}'"
        col = ""
        if self.col > -1:
            col = f" Col {self.col}"
        nro = ""
        if self.nro_line > -1:
            nro = f" Line {self.nro_line}"
        return self.msg + col + nro + ". " + read_so_far + "."


class MAParser:
    def __init__(self):
        self.parser = MAParser.__build_parser()
        self.__init_parse_dict()

    @staticmethod
    def __build_parser():
        keyword_begin_model_name = pp.Literal('[')
        keyword_end_model_name = pp.Literal(']')
        keyword_assign_attribute = pp.Literal(':')
        keyword_comment = pp.Keyword('%')
        keyword_model_instance = pp.Literal('@')
        keyword_link_at = keyword_model_instance
        keyword_components = pp.CaselessKeyword("components")
        keyword_in = pp.CaselessKeyword("in")
        keyword_out = pp.CaselessKeyword("out")
        keyword_link = pp.CaselessKeyword("link")

        value_component_atomic = pp.Word(_MAprintables_)
        value_component_complex = pp.Word(pp.alphas)
        value_component = pp.MatchFirst(value_component_atomic, value_component_complex)
        word_components = keyword_components + keyword_assign_attribute + pp.OneOrMore(
            value_component)
        word_components.setParseAction(lambda s, l, t: [MATokens.COMPONENTS, *t[2:]])

        word_in = keyword_in + keyword_assign_attribute + pp.OneOrMore(pp.Word(_MAprintables_))
        word_in.setParseAction(lambda s, l, t: [MATokens.IN, *t[2:]])
        word_out = keyword_out + keyword_assign_attribute + pp.OneOrMore(pp.Word(_MAprintables_))
        word_out.setParseAction(lambda s, l, t: [MATokens.OUT, *t[2:]])

        value_link_own = pp.Word(_MAprintables_)
        value_link_other = pp.Word(pp.printables) + keyword_link_at + pp.Word(_MAprintables_)
        value_link = pp.Or(value_link_own, value_link_other)
        word_link = keyword_link + keyword_assign_attribute + value_link + value_link
        word_link.setParseAction(lambda s, l, t: [MATokens.LINK, *t[2:]])

        keyword_user_attr = pp.Word(_MAprintables_)
        # Necesario para que no se tome a link como un atributo de usuario
        keyword_user_attr.addCondition(lambda s, loc, toks: toks[0].lower() != "link")
        word_user_attribute = keyword_user_attr + keyword_assign_attribute + pp.OneOrMore(
            pp.Word(_MAprintables_))
        word_user_attribute.setParseAction(lambda s, l, t: [MATokens.ATTR, t[0], *t[2:]])
        word_attribute = word_components("COMPONENTS") | word_in("IN") | word_out(
            "OUT") | word_link("LINK") | word_user_attribute("ATTR")

        word_header = keyword_begin_model_name + pp.Word(pp.alphas) + keyword_end_model_name
        word_header.setParseAction(lambda s, l, t: [MATokens.MODEL_DEF, t[1]])
        word_comment = keyword_comment + pp.ZeroOrMore(pp.Word(pp.printables))
        word_comment.setParseAction(lambda s, l, t: [MATokens.COMMENT, *t[1:]])
        return word_comment("COMMENT") ^ word_header("DEFINITION") ^ word_attribute("ATTRIBUTE")

    @staticmethod
    def empty_context():
        """
        Creates an empty context. A context stores information about MA file
        and checks if its valid
        """
        context = {
            "MODEL_DEFINITIONS": [],
            "MODELS": {},
            "CURRENT_MODEL": None
        }
        return context

    @staticmethod
    def __is_atomic_component(name):
        return name.find("@") != -1

    @staticmethod
    def __get_atomic_name_and_model(name):
        return name.split("@")

    @staticmethod
    def __create_model_structure():
        return {"IS_ATOMIC": True, "COMPONENTS": [], "IN": [], "OUT": [], "LINK": [], "ATTR": []}

    @staticmethod
    def __ma_assert(condition, msg):
        if not condition:
            raise MAParserError(msg)

    def __parse_model_def(self, data, context):
        MAParser.__ma_assert(len(data) > 0, "ERROR: Model definition statement is empty.")
        name = data[0]
        assert name not in context["MODEL_DEFINITIONS"], \
            f"Model name {name} already in use."

        context["MODEL_DEFINITIONS"].append(name)
        context["CURRENT_MODEL"] = name
        context["MODELS"][name] = self.__create_model_structure()
        return context

    def __parse_components_(self, data, context):
        MAParser.__ma_assert(len(data) > 0, "ERROR: Components statement is empty.")

        current_model = context["CURRENT_MODEL"]
        for c in data:
            if self.__is_atomic_component(c):
                local_name, model_name = self.__get_atomic_name_and_model(c)
                to_add = ("ATOMIC", local_name, model_name)
            else:
                to_add = ("COMPOSITE", c)
            context["MODELS"][current_model]["COMPONENTS"].append(to_add)
        context["MODELS"][current_model]["IS_ATOMIC"] = False
        return context

    @staticmethod
    def __parse_in(data, context):
        MAParser.__ma_assert(len(data) > 0, "ERROR: 'in' statement has insufficient parameters.")
        current_model = context["CURRENT_MODEL"]
        context["MODELS"][current_model]["IN"] = data
        return context

    @staticmethod
    def __parse_out(data, context):
        MAParser.__ma_assert(len(data) > 0, "ERROR: 'out' statement has insufficient parameters.")
        current_model = context["CURRENT_MODEL"]
        context["MODELS"][current_model]["OUT"] = data
        return context

    def __parse_link(self, data, context):
        MAParser.__ma_assert(len(data) == 2, "ERROR: 'link' statement has insufficient parameters.")

        current_model = context["CURRENT_MODEL"]
        if self.__is_atomic_component(data[0]):
            port_name, model = self.__get_atomic_name_and_model(data[0])
            in_port = ("REMOTE_PORT", port_name, model)
        else:
            in_port = ("LOCAL_PORT", data[0])
        if self.__is_atomic_component(data[1]):
            port_name, model = self.__get_atomic_name_and_model(data[1])
            out_port = ("REMOTE_PORT", port_name, model)
        else:
            out_port = ("LOCAL_PORT", data[1])

        context["MODELS"][current_model]["LINK"].append((in_port, out_port))
        return context

    @staticmethod
    def __parse_attr(data, context):
        MAParser.__ma_assert(len(data) > 1, "ERROR: Attribute has insufficient parameters.")
        current_model = context["CURRENT_MODEL"]
        name = data[0]
        values = data[1:]
        context["MODELS"][current_model]["ATTR"].append((name, values))
        return context

    def __init_parse_dict(self):
        self.parse_dict = dict()
        self.parse_dict[MATokens.COMMENT] = lambda data, context: context
        self.parse_dict[MATokens.MODEL_DEF] = self.__parse_model_def
        self.parse_dict[MATokens.COMPONENTS] = self.__parse_components_
        self.parse_dict[MATokens.IN] = self.__parse_in
        self.parse_dict[MATokens.OUT] = self.__parse_out
        self.parse_dict[MATokens.LINK] = self.__parse_link
        self.parse_dict[MATokens.ATTR] = self.__parse_attr

    def scan_line(self, line):
        """
        Scans and tokenizes a line of text in MA language.
        :parameter line: A string
        :return: A token generated by the scanner
        """
        try:
            # Era solo espacio en blanco
            if len(line.strip()) == 0:
                return None
            return self.parser.parseString(line)
        except pp.ParseException as e:
            raise MAParserError(f"ERROR: An error ocurred while scanning.", e.col, e.lineno, e.line)

    def scan_text(self, text):
        """
        Scans and tokenizes an entire text.
        :parameter text: A string that contains the MA file text
        :return: the scanned lines as a list
        """
        res = []
        lines = text.splitlines()
        for line in lines:
            scanned_line = self.scan_line(line)
            if scanned_line is not None:
                res.append(scanned_line)
        return res

    @staticmethod
    def __validate_is_valid_model(model_name, context):
        if model_name not in context["MODELS"].keys():
            raise MAParserError("ERROR: Incorrect model definition.")

    @staticmethod
    def __validate_is_atomic(model_name, models_data):
        if models_data[model_name]["IS_ATOMIC"] and \
                len(models_data[model_name]["COMPONENTS"]) > 0:
            raise MAParserError("ERROR: Atomic model cannot have components.")
        if models_data[model_name]["IS_ATOMIC"] and \
                len(models_data[model_name]["IN"]) > 0:
            raise MAParserError("ERROR: Atomic model cannot have 'in' statements.")
        if models_data[model_name]["IS_ATOMIC"] and \
                len(models_data[model_name]["OUT"]) > 0:
            raise MAParserError("ERROR: Atomic model cannot have 'out' statements.")
        if models_data[model_name]["IS_ATOMIC"] and \
                len(models_data[model_name]["LINK"]) > 0:
            raise MAParserError("ERROR: Atomic model cannot have 'link' statements.")

    @staticmethod
    def __validate_is_composite(model_name, models_data):
        if not models_data[model_name]["IS_ATOMIC"] and \
                len(models_data[model_name]["COMPONENTS"]) == 0:
            raise MAParserError("ERROR: Composite model must have at least one component.")

    @staticmethod
    def __validate_composite_components_are_defined(model_name, context):
        for component in context["MODELS"][model_name]["COMPONENTS"]:
            component_name = component[1]
            if component_name not in context["MODEL_DEFINITIONS"]:
                raise MAParserError(f"ERROR: Listed component '{component_name}' is not defined.")

    @staticmethod
    def __validate_composite_links_are_valid(model_name, context):
        def is_valid_port(type, port, model, context):
            if type == "LOCAL_PORT" and \
                    port not in context["MODELS"][model]["IN"] and \
                    port not in context["MODELS"][model]["OUT"]:
                raise MAParserError(f"ERROR: port named '{port}' is not defined for model '{model}'.")
            elif type == "REMOTE_PORT" and \
                    not context["MODELS"][model]["IS_ATOMIC"] and \
                    port not in context["MODELS"][model]["IN"] and \
                    port not in context["MODELS"][model]["OUT"]:
                raise MAParserError(f"ERROR: port named '{port}' is not defined for model '{model}'.")

        for (source_port_desc, dest_port_desc) in context["MODELS"][model_name]["LINK"]:
            source_type, source_port, *source_model = source_port_desc
            dest_type, dest_port, *dest_model = dest_port_desc
            if not source_model:
                source_model = model_name
            else:
                source_model = source_model[0]
            if not dest_model:
                dest_model = model_name
            else:
                dest_model = dest_model[0]
            is_valid_port(source_type, source_port, source_model, context)
            is_valid_port(dest_type, dest_port, dest_model, context)

    @staticmethod
    def __validate_context(context):
        for model_name in context["MODEL_DEFINITIONS"]:
            MAParser.__validate_is_valid_model(model_name, context)
            MAParser.__validate_is_atomic(model_name, context["MODELS"])
            MAParser.__validate_is_composite(model_name, context["MODELS"])
            MAParser.__validate_composite_components_are_defined(model_name, context)
            MAParser.__validate_composite_links_are_valid(model_name, context)

    def parse_line(self, scanned_line, context):
        """
        Parses an already scanned line(a token) and adds it to the context
        :param scanned_line: A token created as a result of scanning
        :param context: Current parsing context
        :return: a modified version of the context
        """
        token_type = scanned_line[0]
        self.parse_dict[token_type](scanned_line[1:], context)
        return context

    def parse_text(self, text):
        """Parses text containing MA code"""
        context = self.empty_context()
        lines = text.splitlines()
        num_line = 0
        try:
            for num, line in enumerate(lines):
                num_line = num
                scanned_line = self.scan_line(line)
                if scanned_line is not None:
                    print(self.parse_line(scanned_line, context))
            self.__validate_context(context)
        except MAParserError as e:
            raise MAParserError(e.msg, e.col, num_line, e.line)
        return context

    def parse_file(self, filename):
        """Parses an entire MA file"""
        with open(filename, 'r') as f:
            lines = f.read()
            context = self.parse_text(lines)
        return context
