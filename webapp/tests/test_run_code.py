from io import StringIO

import pytest

from webapp.src.main import run_code


@pytest.mark.parametrize('code, input_data, result', [
    ("print('Hello, World!')", '', 'Hello, World!\n'),
    ("print(2**3)", '', '8\n'),
    ("import math\nprint(round(math.pi, 2))", '', '3.14\n'),
])
def test_positive_case(code, input_data, result):
    assert run_code(code, input_data=input_data, number=1) == \
           {'color': 'black', 'number': 1, 'result': result}


@pytest.mark.parametrize('code, input_data, result', [
    ("a = input('-->')\nprint(a)", 'python', '-->python\n'),
    ("a = input()\nprint(a)", '2+1', '2+1\n'),
    ("a = int(input())\nprint(a)", '2', "2\n"),
])
def test_input_case(monkeypatch, code, input_data, result):
    _input = StringIO(input_data)
    monkeypatch.setattr('sys.stdin', _input)
    assert run_code(code, input_data=input_data, number=1) == \
           {'color': 'black', 'number': 1, 'result': result}


@pytest.mark.parametrize('code, input_data, err', [
    ("a = 1 / 0", '', 'ZeroDivisionError: division by zero\n'),
    ("1a = 1", '', 'SyntaxError: invalid syntax\n'),
    ("object.hello", '', 'AttributeError: type object \'object\' has no attribute \'hello\'\n'),
])
def test_error_case(code, input_data, err):
    assert run_code(code, input_data=input_data, number=1)['result'].endswith(err)


@pytest.mark.parametrize('code, input_data, err', [
    ("open('EVE.txt', 'w')", '', 'ValueError: open is not allowed in this code\n'),
    ("eval(2+3)", '', 'ValueError: eval is not allowed in this code\n'),
    ("exec(2+3)", '', 'ValueError: exec is not allowed in this code\n'),
])
def test_open_exec_eval_case(code, input_data, err):
    assert run_code(code, input_data=input_data, number=1)['result'].endswith(err)


@pytest.mark.parametrize('code, input_data, err', [
    ("import os", '', 'ValueError: os is not allowed in this code\n'),
    ("import shutil", '', 'ValueError: shutil is not allowed in this code\n'),
    ("import flask", '', 'ValueError: flask is not allowed in this code\n'),
])
def test_import_case(code, input_data, err):
    assert run_code(code, input_data=input_data, number=1)['result'].endswith(err)


def test__import__case():
    code = 'os = "o" + "s"\n__import__(os)'
    err = 'ValueError: __import__ is not allowed in this code\n'
    assert run_code(code, input_data='', number=1)['result'].endswith(err)


@pytest.mark.parametrize('code, result', [
    ("print('open the door')", 'open the door\n'),
    ("print('os - standard pkg')", 'os - standard pkg\n'),
])
def test_open(code, result):
    assert run_code(code, input_data='', number=1) == \
           {'color': 'black', 'number': 1, 'result': result}
