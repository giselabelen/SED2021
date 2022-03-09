from DEVSParser.src import MAParser
import pytest


@pytest.fixture
def parser():
    return MAParser.MAParser()


def test_scan_line_empty(parser):
    with pytest.raises(MAParser.MAParserError) as e_info:
        parser.scan_line("")


def test_scan_line_comment_empty(parser):
    assert parser.scan_line("%")["COMMENT"][0:1] == ["%"]


def test_scan_line_comment_simple(parser):
    assert parser.scan_line("% test comment")["COMMENT"][0:3] == ["%", "test", "comment"]


def test_scan_line_simple_header(parser):
    assert parser.scan_line("[ hello ]")["DEFINITION"][0:3] == ["[", "hello", "]"]


def test_scan_line_simple_header_no_whitespace(parser):
    assert parser.scan_line("[hello]")["DEFINITION"][0:3] == ["[", "hello", "]"]


def test_scan_line_simple_components(parser):
    assert parser.scan_line("components : test")["COMPONENTS"][0:3] == ["components", ":", "test"]


def test_scan_line_complex_components(parser):
    assert parser.scan_line("components : test@generator")["COMPONENTS"][0:3] == ["components", ":", "test@generator"]


def test_scan_line_simple_in(parser):
    assert parser.scan_line("in : port")["IN"][0:3] == ["in", ":", "port"]


def test_scan_line_complex_in(parser):
    assert parser.scan_line("in : port1 port2")["IN"][0:4] == ["in", ":", "port1", "port2"]


def test_scan_line_simple_out(parser):
    assert parser.scan_line("out : port")["OUT"][0:3] == ["out", ":", "port"]


def test_scan_line_complex_out(parser):
    assert parser.scan_line("out : port1 port2")["OUT"][0:4] == ["out", ":", "port1", "port2"]


def test_scan_line_outgoing_link(parser):
    assert parser.scan_line("link : port port@test")["LINK"][0:4] == ["link", ":", "port", "port@test"]


def test_scan_line_incoming_link(parser):
    assert parser.scan_line("link : port@test port ")["LINK"][0:4] == ["link", ":", "port@test", "port"]


def test_scan_line_user_attribute(parser):
    assert parser.scan_line("distribution : normal")["ATTRIBUTE"][0:3] == ["distribution", ":", "normal"]

