from DEVSParser.src import MAParser
import pytest
from . import examples


@pytest.fixture
def parser():
    return MAParser.MAParser()


@pytest.fixture
def context():
    return MAParser.MAParser._create_context_()

#
# scan_line_tests
#


def test_scan_line_empty(parser):
    assert parser.scan_line("") is None


def test_scan_line_comment_empty(parser):
    assert parser.scan_line("%")[0:1] == ["COMMENT"]


def test_scan_line_comment_simple(parser):
    assert parser.scan_line("% test comment")[0:3] == ["COMMENT", "test", "comment"]


def test_scan_line_simple_header(parser):
    assert parser.scan_line("[ hello ]")[0:2] == ["MODEL_DEF", "hello"]


def test_scan_line_simple_header_no_whitespace(parser):
    assert parser.scan_line("[hello]")[0:2] == ["MODEL_DEF", "hello"]


def test_scan_line_complex_header(parser):
    assert parser.scan_line("[ helloWorld ]")[0:2] == ["MODEL_DEF", "helloWorld"]


def test_scan_line_simple_components(parser):
    assert parser.scan_line("components : test")[0:3] == ["COMPONENTS", "test"]


def test_scan_line_complex_components(parser):
    assert parser.scan_line("components : test@generator")[0:3] == ["COMPONENTS", "test@generator"]


def test_scan_line_simple_in(parser):
    assert parser.scan_line("in : port")[0:3] == ["IN", "port"]


def test_scan_line_complex_in(parser):
    assert parser.scan_line("in : port1 port2")[0:4] == ["IN", "port1", "port2"]


def test_scan_line_simple_out(parser):
    assert parser.scan_line("out : port")[0:3] == ["OUT", "port"]


def test_scan_line_complex_out(parser):
    assert parser.scan_line("out : port1 port2")[0:4] == ["OUT", "port1", "port2"]


def test_scan_line_outgoing_link(parser):
    assert parser.scan_line("link : port port@test")[0:4] == ["LINK", "port", "port@test"]


def test_scan_line_incoming_link(parser):
    assert parser.scan_line("link : port@test port ")[0:4] == ["LINK", "port@test", "port"]


def test_scan_line_user_attribute(parser):
    assert parser.scan_line("distribution : normal")[0:3] == ["ATTR", "distribution", "normal"]


#
# scan_text_tests
#
def test_scan_text_example_simple(parser):
    scanned_text = parser.scan_text(examples.EXAMPLE_SIMPLE)
    assert len(scanned_text) == 12
    assert scanned_text[0][0:2] == ["MODEL_DEF", "top"]
    assert scanned_text[1][0:2] == ["COMPONENTS", "generator@generator"]
    assert scanned_text[2][0:2] == ["OUT", "out_port"]
    assert scanned_text[3][0:2] == ["IN", "stop"]
    assert scanned_text[4][0:3] == ["LINK", "stop", "stop@generator"]
    assert scanned_text[5][0:3] == ["LINK", "out@generator", "out_port"]
    assert scanned_text[6][0:2] == ["MODEL_DEF", "generator"]
    assert scanned_text[7][0:3] == ["ATTR", "distribution", "normal"]
    assert scanned_text[8][0:3] == ["ATTR", "mean", "3"]
    assert scanned_text[9][0:3] == ["ATTR", "deviation", "1"]
    assert scanned_text[10][0:3] == ["ATTR", "initial", "1"]
    assert scanned_text[11][0:3] == ["ATTR", "increment", "5"]

#
# parse_line_tests
#


def test_parse_line_comment(parser, context):
    """Parsing a comment does not affect the context"""
    context = parser.parse_line(parser.scan_line("%"), context)
    assert not context["MODEL_DEFINITIONS"]
    assert not context["MODELS"]
    assert not context["CURRENT_MODEL"]


def test_parse_line_model_def(parser, context):
    """
    Parsing a model definition adds a new model to the context and
    sets it as the current one.
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    assert "test" in context["MODEL_DEFINITIONS"]
    assert context["CURRENT_MODEL"] == "test"
    assert context["MODELS"]["test"]


def test_parse_line_model_def_current_model(parser, context):
    """
    Parsing a model definition adds a new model to the context and
    sets it as the current one.
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("[testdos]"), context)
    assert "test" in context["MODEL_DEFINITIONS"]
    assert "testdos" in context["MODEL_DEFINITIONS"]
    assert context["CURRENT_MODEL"] == "testdos"
    assert context["MODELS"]["test"]
    assert context["MODELS"]["testdos"]


def test_parse_line_components_composite(parser, context):
    """
    Parsing a components statement adds them to the current model subcomponents
    list and marks the current model as non-atomic.
    The subcomponent added is composite.
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("components : test2"), context)
    assert ("COMPOSITE", "test2") in context["MODELS"]["test"]["COMPONENTS"]
    assert not context["MODELS"]["test"]["IS_ATOMIC"]


def test_parse_line_components_atomic(parser, context):
    """
    Parsing a components statement adds them to the current model subcomponents
    list and marks the current model as non-atomic.
    The subcomponent added is atomic.
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("components : t@Test2"), context)
    assert ("ATOMIC", "t", "Test2") in context["MODELS"]["test"]["COMPONENTS"]
    assert not context["MODELS"]["test"]["IS_ATOMIC"]


def test_parse_line_components_mixed(parser, context):
    """
    Parsing a components statement adds them to the current model subcomponents
    list and marks the current model as non-atomic.
    The subcomponents added may be atomic or composite.
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("components : t@Test2 t2 t3@Test4 t5"), context)
    assert ("ATOMIC", "t", "Test2") in context["MODELS"]["test"]["COMPONENTS"]
    assert ("COMPOSITE", "t2") in context["MODELS"]["test"]["COMPONENTS"]
    assert ("ATOMIC", "t3", "Test4") in context["MODELS"]["test"]["COMPONENTS"]
    assert ("COMPOSITE", "t5") in context["MODELS"]["test"]["COMPONENTS"]
    assert not context["MODELS"]["test"]["IS_ATOMIC"]


def test_parse_line_in_simple(parser, context):
    """
    Parsing a in statement adds the listed ports to the current model in-ports list
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("in : test1"), context)
    assert "test1" in context["MODELS"]["test"]["IN"]


def test_parse_line_in_complex(parser, context):
    """
    Parsing a in statement adds the listed ports to the current model in-ports list
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("in : test1 test2 test3"), context)
    assert "test1" in context["MODELS"]["test"]["IN"]
    assert "test2" in context["MODELS"]["test"]["IN"]
    assert "test3" in context["MODELS"]["test"]["IN"]


def test_parse_line_out_simple(parser, context):
    """
    Parsing an out statement adds the listed ports to the current model out-ports list
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("out : test1"), context)
    assert "test1" in context["MODELS"]["test"]["OUT"]


def test_parse_line_out_complex(parser, context):
    """
    Parsing an out statement adds the listed ports to the current model out-ports list
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("out : test1 test2 test3"), context)
    assert "test1" in context["MODELS"]["test"]["OUT"]
    assert "test2" in context["MODELS"]["test"]["OUT"]
    assert "test3" in context["MODELS"]["test"]["OUT"]


def test_parse_line_link_outgoing(parser, context):
    """
    Parsing a link statement adds the pair (from_port, to_port) to the current model
    links lists.
    This case link goes from a local port to a remote port.
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("link : out in@Test"), context)
    assert len(context["MODELS"]["test"]["LINK"]) == 1
    port_pair = context["MODELS"]["test"]["LINK"][0]
    assert ("LOCAL_PORT", "out") == port_pair[0]
    assert ("REMOTE_PORT", "in", "Test") == port_pair[1]


def test_parse_line_link_incoming(parser, context):
    """
    Parsing a link statement adds the pair (from_port, to_port) to the current model
    links lists.
    This case link goes from a remote port to a local port.
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("link : out@Test in"), context)
    assert len(context["MODELS"]["test"]["LINK"]) == 1
    port_pair = context["MODELS"]["test"]["LINK"][0]
    assert ("REMOTE_PORT", "out", "Test") == port_pair[0]
    assert ("LOCAL_PORT", "in") == port_pair[1]


def test_parse_line_link_mixed(parser, context):
    """
    Parsing a link statement adds the pair (from_port, to_port) to the current model
    links lists.
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("link : out@Test in"), context)
    assert len(context["MODELS"]["test"]["LINK"]) == 1
    first_port_pair = context["MODELS"]["test"]["LINK"][0]
    assert ("REMOTE_PORT", "out", "Test") == first_port_pair[0]
    assert ("LOCAL_PORT", "in") == first_port_pair[1]
    context = parser.parse_line(parser.scan_line("link : out@Test in"), context)
    assert len(context["MODELS"]["test"]["LINK"]) == 2
    second_port_pair = context["MODELS"]["test"]["LINK"][1]
    assert ("REMOTE_PORT", "out", "Test") == second_port_pair[0]
    assert ("LOCAL_PORT", "in") == second_port_pair[1]


def test_parse_line_attr_single_value_(parser, context):
    """
    Parsing an attribute adds it to the current model attribute list
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("distribution : normal"), context)
    assert len(context["MODELS"]["test"]["ATTR"]) == 1
    assert ("distribution", ["normal"]) in context["MODELS"]["test"]["ATTR"]


def test_parse_line_attr_complex_(parser, context):
    """
    Parsing an attribute adds it to the current model attribute list
    """
    context = parser.parse_line(parser.scan_line("[test]"), context)
    context = parser.parse_line(parser.scan_line("distribution : normal"), context)
    context = parser.parse_line(parser.scan_line("mean : 3"), context)
    context = parser.parse_line(parser.scan_line("deviation : 1"), context)
    context = parser.parse_line(parser.scan_line("initial : 1"), context)
    assert len(context["MODELS"]["test"]["ATTR"]) == 4
    assert ("distribution", ["normal"]) in context["MODELS"]["test"]["ATTR"]
    assert ("mean", ["3"]) in context["MODELS"]["test"]["ATTR"]
    assert ("deviation", ["1"]) in context["MODELS"]["test"]["ATTR"]
    assert ("initial", ["1"]) in context["MODELS"]["test"]["ATTR"]


def test_scan_line_empty_statements_cause_exceptions(parser):
    """
    Empty statements or with insufficient parameters cause exceptions
    """
    with pytest.raises(Exception) as exc_info:
        parser.scan_line("[]")
    with pytest.raises(Exception) as exc_info:
        parser.scan_line("components : ")
    with pytest.raises(Exception) as exc_info:
        parser.scan_line("in : ")
    with pytest.raises(Exception) as exc_info:
        parser.scan_line("out : ")
    with pytest.raises(Exception) as exc_info:
        parser.scan_line("link : ")
    with pytest.raises(Exception) as exc_info:
        parser.scan_line("link : test")
    with pytest.raises(Exception) as exc_info:
        parser.scan_line("link : t@test")
    with pytest.raises(Exception) as exc_info:
        parser.scan_line("distribution : ")
