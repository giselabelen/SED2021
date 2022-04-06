import pyparsing as pp
from enum import Enum


class MAParserError(Exception):
    def __init__(self, msg="MAParser error"):
        self.msg = msg
        super().__init__(msg)


class MAParser:
    def __init__(self):
        self.keyword_begin_model_name = pp.Literal('[')
        self.keyword_end_model_name = pp.Literal(']')
        self.keyword_assign_attribute = pp.Keyword(':')
        self.keyword_comment = pp.Keyword('%')
        self.keyword_model_instance = pp.Literal('@')
        self.keyword_link_at = self.keyword_model_instance
        self.keyword_components = pp.CaselessKeyword("components")
        self.keyword_in = pp.CaselessKeyword("in")
        self.keyword_out = pp.CaselessKeyword("out")
        self.keyword_link = pp.CaselessKeyword("link")

        self.value_component_atomic = pp.Word(pp.printables)
        self.value_component_complex = pp.Word(pp.alphas)
        self.value_component = pp.MatchFirst(self.value_component_atomic, self.value_component_complex)
        self.word_components = self.keyword_components + self.keyword_assign_attribute + pp.OneOrMore(
            self.value_component)
        self.word_components.setParseAction(lambda s, l, t: ["COMPONENTS", *t[2:]])

        self.word_in = self.keyword_in + self.keyword_assign_attribute + pp.OneOrMore(pp.Word(pp.printables))
        self.word_in.setParseAction(lambda s, l, t: ["IN", *t[2:]])
        self.word_out = self.keyword_out + self.keyword_assign_attribute + pp.OneOrMore(pp.Word(pp.printables))
        self.word_out.setParseAction(lambda s, l, t: ["OUT", *t[2:]])

        self.value_link_own = pp.Word(pp.printables)
        self.value_link_other = pp.Word(pp.printables) + self.keyword_link_at + pp.Word(pp.printables)
        self.value_link = pp.Or(self.value_link_own, self.value_link_other)
        self.word_link = self.keyword_link + self.keyword_assign_attribute + self.value_link + self.value_link
        self.word_link.setParseAction(lambda s, l, t: ["LINK", *t[2:]])

        self.keyword_user_attr = pp.Word(pp.printables)
        # Necesario para que no se tome a link como un atributo de usuario
        self.keyword_user_attr.addCondition(lambda s, loc, toks: toks[0].lower() != "link")
        self.word_user_attribute = self.keyword_user_attr + self.keyword_assign_attribute + pp.OneOrMore(
            pp.Word(pp.printables))
        self.word_user_attribute.setParseAction(lambda s, l, t: ["ATTR", t[0], *t[2:]])
        self.word_attribute = self.word_components("COMPONENTS") | self.word_in("IN") | self.word_out(
            "OUT") | self.word_link("LINK") | self.word_user_attribute("ATTR")

        self.word_header = self.keyword_begin_model_name + pp.Word(pp.alphas) + self.keyword_end_model_name
        self.word_header.setParseAction(lambda s, l, t: ["MODEL_DEF", t[1]])
        self.word_comment = self.keyword_comment + pp.ZeroOrMore(pp.Word(pp.printables))
        self.word_comment.setParseAction(lambda s, l, t: ["COMMENT", *t[1:]])

        self.parser = self.word_comment("COMMENT") ^ self.word_header("DEFINITION") ^ self.word_attribute("ATTRIBUTE")
        self._init_parse_dict_()

    @staticmethod
    def _create_context_():
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
    def _is_atomic_component_(name):
        return name.find("@") != -1

    @staticmethod
    def _get_atomic_name_and_model_(name):
        return name.split("@")

    @staticmethod
    def _create_model_structure_():
        return {"IS_ATOMIC": True, "COMPONENTS": [], "IN": [], "OUT": [], "LINK": [], "ATTR": []}

    def _parse_model_def_(self, data, context):
        assert len(data) > 0, "Model definition statement is empty"
        name = data[0]
        assert name not in context["MODEL_DEFINITIONS"],\
            f"Model name {name} already in use."

        context["MODEL_DEFINITIONS"].append(name)
        context["CURRENT_MODEL"] = name
        context["MODELS"][name] = self._create_model_structure_()
        return context

    def _parse_components_(self, data, context):
        assert len(data) > 0, "Components statement is empty"

        current_model = context["CURRENT_MODEL"]
        for c in data:
            if self._is_atomic_component_(c):
                local_name, model_name = self._get_atomic_name_and_model_(c)
                to_add = ("ATOMIC", local_name, model_name)
            else:
                to_add = ("COMPOSITE", c)
            context["MODELS"][current_model]["COMPONENTS"].append(to_add)
        context["MODELS"][current_model]["IS_ATOMIC"] = False
        return context

    def _parse_in_(self, data, context):
        assert len(data) > 0, "In statement has insufficient parameters"
        current_model = context["CURRENT_MODEL"]
        context["MODELS"][current_model]["IN"] = data
        return context

    def _parse_out_(self, data, context):
        assert len(data) > 0, "Out statement has insufficient parameters"
        current_model = context["CURRENT_MODEL"]
        context["MODELS"][current_model]["OUT"] = data
        return context

    def _parse_link_(self, data, context):
        assert len(data) == 2, "Link statement has insufficient parameters"

        current_model = context["CURRENT_MODEL"]
        if self._is_atomic_component_(data[0]):
            port_name, model = self._get_atomic_name_and_model_(data[0])
            in_port = ("REMOTE_PORT", port_name, model)
        else:
            in_port = ("LOCAL_PORT", data[0])
        if self._is_atomic_component_(data[1]):
            port_name, model = self._get_atomic_name_and_model_(data[1])
            out_port = ("REMOTE_PORT", port_name, model)
        else:
            out_port = ("LOCAL_PORT", data[1])

        context["MODELS"][current_model]["LINK"].append((in_port, out_port))
        return context

    def _parse_attr_(self, data, context):
        assert len(data) > 1, "Attribute has insufficient parameters"
        current_model = context["CURRENT_MODEL"]
        name = data[0]
        values = data[1:]
        context["MODELS"][current_model]["ATTR"].append((name, values))
        return context

    def _init_parse_dict_(self):
        self.parse_dict = dict()
        self.parse_dict["COMMENT"] = lambda data, context: context
        self.parse_dict["MODEL_DEF"] = self._parse_model_def_
        self.parse_dict["COMPONENTS"] = self._parse_components_
        self.parse_dict["IN"] = self._parse_in_
        self.parse_dict["OUT"] = self._parse_out_
        self.parse_dict["LINK"] = self._parse_link_
        self.parse_dict["ATTR"] = self._parse_attr_

    def scan_line(self, line):
        """
        Scans and tokenizes a line of text in MA language.
        :parameter text: A string
        :return: A token generated by the scanner
        """
        try:
            # Era solo espacio en blanco
            if len(line.strip()) == 0:
                return None
            return self.parser.parseString(line)
        except pp.ParseException as e:
            raise MAParserError

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
    def _validate_is_valid_model_(model_name, context):
        if model_name not in context["MODELS"].keys():
            raise MAParserError("ERROR: Incorrect model definition")

    @staticmethod
    def _validate_is_atomic_(model_name, models_data):
        if models_data[model_name]["IS_ATOMIC"] and \
                len(models_data[model_name]["COMPONENTS"]) > 0:
            raise MAParserError("ERROR: Atomic model cannot have components.")
        if models_data[model_name]["IS_ATOMIC"] and \
            len(models_data[model_name]["IN"]) > 0:
            raise MAParserError("ERROR: Atomic model cannot have IN statements.")
        if models_data[model_name]["IS_ATOMIC"] and \
            len(models_data[model_name]["OUT"]) > 0:
            raise MAParserError("ERROR: Atomic model cannot have OUT statements.")
        if models_data[model_name]["IS_ATOMIC"] and \
            len(models_data[model_name]["LINK"]) > 0:
            raise MAParserError("ERROR: Atomic model cannot have LINK statements.")

    @staticmethod
    def _validate_is_composite_(model_name, models_data):
        if not models_data[model_name]["IS_ATOMIC"] and \
            len(models_data[model_name]["COMPONENTS"]) == 0:
            raise MAParserError("ERROR: Composite model must have at least one component.")

    @staticmethod
    def _validate_composite_components_are_defined_(model_name, context):
        for component in context["MODELS"][model_name]["COMPONENTS"]:
            component_name = component[1]
            if component_name not in context["MODEL_DEFINITIONS"]:
                raise MAParserError(f"ERROR: Listed component {component_name} in not defined")

    @staticmethod
    def _validate_composite_links_are_valid_(model_name, context):
        def is_valid_port(type, port, model, context):
            if type == "LOCAL_PORT" and \
                port not in context["MODELS"][model]["IN"] and \
                port not in context["MODELS"][model]["OUT"]:
                raise MAParserError(f"ERROR: port name {port} is not defined for model {model}")
            elif type == "REMOTE_PORT" and \
                not context["MODELS"][model]["IS_ATOMIC"] and \
                port not in context["MODELS"][model]["IN"] and \
                port not in context["MODELS"][model]["OUT"]:
                raise MAParserError(f"ERROR: port name {port} is not defined for model {model}")
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


    def validate_context(self, context):
        for model_name in context["MODEL_DEFINITIONS"]:
            MAParser._validate_is_valid_model_(model_name, context)
            MAParser._validate_is_atomic_(model_name, context["MODELS"])
            MAParser._validate_is_composite_(model_name, context["MODELS"])
            MAParser._validate_composite_components_are_defined_(model_name, context)
            MAParser._validate_composite_links_are_valid_(model_name, context)

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
        context = self._create_context_()
        lines = text.splitlines()
        for line in lines:
            scanned_line = self.scan_line(line)
            if scanned_line is not None:
                print(self.parse_line(scanned_line, context))
        self.validate_context(context)
        return context

    def parse_file(self, filename):
        """Parses an entire MA file"""
        context = self._create_context_()
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(self.parse_line(self.scan_line(line), context))
        self.validate_context(context)
        return context