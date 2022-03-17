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


def test_parse_line_components(parser, context):
    """
    Parsing a model definition adds a new model to the context and
    sets it as the current one.
    """
    pass
