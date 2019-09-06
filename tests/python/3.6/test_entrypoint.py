import os
import pytest
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import src.entrypoint as entrypoint

build = entrypoint.get_constant(*entrypoint.constants.build_directory)
workspace = entrypoint.get_constant(*entrypoint.constants.workspace)
BUILD_DIR = f'{workspace}/{build}'

@pytest.fixture
def remove_build_dir():
    def remove():
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
        assert os.path.exists(BUILD_DIR) is False
    return remove

def test_get_constant(monkeypatch):
    assert entrypoint.get_constant('LAMBDA_CODE_DIR', 'src') == '/src'
    assert entrypoint.get_constant(*entrypoint.constants.workspace) == '/'
    assert entrypoint.get_constant(*entrypoint.constants.build_directory) == '/package'

    monkeypatch.setenv('LAMBDA_CODE_DIR', '/tests/src')
    assert entrypoint.get_constant(*entrypoint.constants.code_dir) == '/tests/src'
    monkeypatch.delenv('LAMBDA_CODE_DIR')

    assert entrypoint.get_constant('LAMBDA_CODE_DIR', '/../../src') == '/src'
    assert entrypoint.get_constant('LAMBDA_CODE_DIR', '/./../src') == '/src'
    assert entrypoint.get_constant('LAMBDA_CODE_DIR', '../../src') == '/src'

    cwd = os.getcwd()
    os.chdir('/tests')
    assert entrypoint.get_constant('LAMBDA_CODE_DIR', '../../src') == '/tests/src'
    os.chdir(cwd)

def test_copy_source_to_build(monkeypatch, remove_build_dir):
    remove_build_dir()
    monkeypatch.setenv('LAMBDA_CODE_DIR', '/tests/src')
    entrypoint.copy_source_to_build()
    assert os.path.exists(f'{BUILD_DIR}/lambda_function.py')
    assert os.path.exists(f'{BUILD_DIR}/requirements.txt')
    remove_build_dir()
    monkeypatch.setenv('PRESERVE_ROOT', 'True')
    entrypoint.copy_source_to_build()
    assert os.path.exists(f'{BUILD_DIR}/src/lambda_function.py')
    assert os.path.exists(f'{BUILD_DIR}/src/requirements.txt')
    remove_build_dir()

@patch('subprocess.Popen')
def test_install_dependencies(popen, monkeypatch, remove_build_dir):
    remove_build_dir()
    with  tempfile.NamedTemporaryFile(delete=False) as stdout_mock:
        stdout_mock.write(b'STDOUT (mocked)')
        stdout_mock.seek(0)
        popen.return_value.stdout = stdout_mock
        popen.return_value.poll.return_value = 0
        monkeypatch.setenv('LAMBDA_CODE_DIR', '/tests/src')
        monkeypatch.setenv('REQUIREMENTS_FILE', 'requirements.txt')
        entrypoint.copy_source_to_build()
        assert entrypoint.install_dependencies() is 0

    assert popen.called
    remove_build_dir()

def test_package_contents(monkeypatch, remove_build_dir):
    remove_build_dir()
    monkeypatch.setenv('LAMBDA_CODE_DIR', '/tests/src')
    monkeypatch.setenv('REQUIREMENTS_FILE', 'requirements.txt')
    entrypoint.copy_source_to_build()
    assert entrypoint.package_contents()
    assert os.path.exists('/package.zip')
    remove_build_dir()
