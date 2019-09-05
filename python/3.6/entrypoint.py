import logging
import os
import shutil
import sys
import subprocess
from types import SimpleNamespace
from pathlib import Path
import zipfile


logging.basicConfig(
    level=logging.DEBUG if os.environ.get('DEBUG') else logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_constant(key: str, default_value: str):
    '''
    get value from ENVIRONMENT and ignore invalid characters
    '''
    value = os.getenv(key, default_value)
    try:
        value = value.encode('ascii', 'ignore').decode('ascii')
    except AttributeError as error:
        if 'bool' not in str(error):
            raise error

    if isinstance(value, str):
        value = os.path.normpath(value)

    logging.debug('get_constant(%s, %s)', key, value)
    # test_path = (Path(CWD) / value).resolve()
    # if test_path.parent != Path(basedir).resolve():
    #     raise PermissionError(f'Filename {test_path} is not in {Path(CWD)} directory')
    return value

constants = SimpleNamespace(
    code_dir=('LAMBDA_CODE_DIR', 'src'),
    artifact_name=('ARTIFACT_NAME', 'deployment.zip'),
    build_directory=('CONTAINER_BUILD_DIRECTORY', './package'),
    workspace=('CI_WORKSPACE', os.getcwd()),
    requirements_file=('REQUIREMENTS_FILE', 'requirements.txt'),
    preserve_root=('PRESERVE_ROOT', False),
)

def copy_source_to_build():
    '''
    Copy the src folder into build
    '''
    root = get_constant(*constants.workspace)
    code = get_constant(*constants.code_dir)
    build = get_constant(*constants.build_directory)
    workspace = get_constant(*constants.workspace)
    source = f'{root}/{code}'
    destination = f'{workspace}/{build}'

    if get_constant(*constants.preserve_root):
        destination += f'/{os.path.basename(source)}'

    shutil.copytree(
        src=source,
        dst=destination,
    )

def install_dependencies():
    '''
    Install pip dependencies
    '''
    logging.info('installing dependencies')
    requirements = get_constant(*constants.requirements_file)
    code = get_constant(*constants.code_dir)
    build = get_constant(*constants.build_directory)
    workspace = get_constant(*constants.workspace)
    logging.info(f'pip install -r {code}/{requirements} -t {workspace}/{build}')
    p = subprocess.Popen(
        f'pip install -r {code}/{requirements} -t {workspace}/{build}',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    exit_code = None
    while True:
        out = p.stdout.read(1)
        exit_code = p.poll()
        if not out and exit_code != None:
            break
        if out != '':
            sys.stdout.write(out.decode('ascii'))
            sys.stdout.flush()

    return exit_code

def package_contents():
    '''
    zip file contents within a zip file to new file directory
    file: zipped file
    '''
    logging.info('Begin: rezipping file contents...')
    build = get_constant(*constants.build_directory)
    workspace = get_constant(*constants.workspace)
    target_path = f'{workspace}/{build}'
    file = f'{target_path}.zip'
    with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as new_zip:
        for root, _, files in os.walk(target_path):
            for fileName in files:
                abspath = os.path.join(root, fileName)
                new_zip.write(abspath, abspath.replace(target_path, ''))
    logging.info('End: file contents rezipped')
    return file

## Actually doing things
def main():
    logging.info('start')
    copy_source_to_build()
    if install_dependencies() != 0:
        raise Exception('NonZero exit code when installing dependencies')
    logging.info('done')

# cd ${BUILD_DIR}
# [ -e ${REQUIREMENTS_FILE} ] && pip install -r ${REQUIREMENTS_FILE} -t ./
# chmod -R 755 .
# zip -r9 ${WORKSPACE}/${ARTIFACT} * -x '*.pyc' -x ${REQUIREMENTS_FILE} -x '${ARTIFACT}'

if __name__ == '__main__':
    main()
