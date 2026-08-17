"""tests/test_log_parser_py.py — FROZEN. Not edited during a drill.

Write every case yourself. AI may write fixtures plumbing; it may not write a case.
"""
import pytest
from log_parser_py import scan, main


def test_range_rides_boundry():
    r = scan(["0,48", "10,50", "20,48"], max_ok = 50, window_ms = 100)
    assert r.violated is False
    assert r.worst_ms == 10
    
    r = scan(["0,48", "10,53", "20,50", "30,53", "40,48"], max_ok = 50, window_ms = 100)
    assert r.violated is False
    assert r.worst_ms == 30
    
def test_excursion_shorter_and_at_window():
    r = scan(["0,48", "10,53", "20,58", "30,53", "40,48"], max_ok = 50, window_ms = 30)
    assert r.violated is True
    assert r.worst_ms == 30
    
    r = scan(["0,48", "10,53", "20,54", "30,48"], max_ok = 50, window_ms = 30)
    assert r.violated is False
    assert r.worst_ms == 20
    
def test_excursion_open_at_file_end():
    r = scan(["0,48", "10,53", "20,54", "30,58"], max_ok = 50, window_ms = 20)
    assert r.violated is True
    assert r.worst_ms == 20
    
def test_line_errors(tmp_path):
    p = tmp_path / "telemetry.log"
    
    # truncated line
    p.write_text("0,48\n10,53\n20,54\n30,")
    assert main(["50", "20", str(p)]) == 2
    
    # blank line
    p.write_text("0,48\n\n20,54\n30,58\n")
    assert main(["50", "20", str(p)]) == 2

    # wrong field count line
    p.write_text("0,48\n10,53,100\n20,54\n30,58\n")
    assert main(["50", "20", str(p)]) == 2

def test_empty_file_and_file_with_only_a_header(tmp_path):
    p = tmp_path / "telemetry.log"
    
    # empty file
    p.write_text("")
    assert main(["50", "20", str(p)]) == 2
    
    # file with only header
    p.write_text("timestamp,value\n")
    assert main(["50", "20", str(p)]) == 2
    
def test_one_million_lines():
    lines = (f"{i * 10},20\n" for i in range(1000000)) # generator expression (comprehension form - statement form is normal for loop with yield)
    r = scan(lines, max_ok = 50, window_ms = 30)
    assert r.violated is False
    