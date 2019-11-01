#!/usr/bin/python
import configparser
import glob
import os
import re
import subprocess
import sys
import tempfile
import argparse

import yaml


regex = re.compile(r'/blueprint.ya?ml$')


def redtext(message):
    return "\033[0;31m{}\033[0m".format(message)


def greentext(message):
    return "\033[0;32m{}\033[0m".format(message)


def errormsg(message):
    print(redtext("ERROR: {}".format(message)))

def load_testdef_from_yaml_file(yaml_file):
    """
    Given a path to a yaml, return the its contents as a dictionary.
    """
    testdef = {}
    try:
        with open(yaml_file) as contents:
            testdef = yaml.load(contents, Loader=yaml.Loader)
        if testdef is None:
            testdef = {}
    except Exception as e:
        errormsg(e)
        sys.exit(1)

    return testdef


def validate_testdef(testdef):
    """
    Validate the given testdef dictionary for required keys.
    """
    if 'answers-file' not in testdef:
        errormsg("Missing 'answers-file' key in test definition")
        sys.exit(1)

    if 'expected-files' in testdef and 'not-expected-files' in testdef:
        duplicates = [duplicate for duplicate in testdef['expected-files'] if duplicate in testdef['not-expected-files']]
        if duplicates:
            for duplicate in duplicates:
                errormsg("Filename {} appears in both 'expected-files' and 'not-expected-files' sections".format(duplicate))
            sys.exit(1)


def identify_missing_files(expected_files):
    """
    Extract the missing files from all those we expected to find.
    """
    return [filename for filename in expected_files if not os.path.exists('{}'.format(filename))]


def identify_not_missing_files(not_expected_files):
    """
    Identify any files we weren't expecting to find.
    """
    return [filename for filename in not_expected_files if os.path.exists('{}'.format(filename))]


def parse_xlvals_file(filepath):
    """
    Since .xlvals files are not true .ini files, we:
    - read the file contents into a string
    - prepend '[default]' to make in a valid .ini file
    - parse it as a config file
    """
    data = ""
    with open(filepath) as xlvals:
        data = '[default]\n{}'.format(xlvals.read())

    config = configparser.ConfigParser()
    config.read_string(data)
    return config


def type_aware_equals(expected, actual):
    """
    Use the type of expected to convert actual before comparing.
    """
    if type(expected) == int:
        try:
            return expected == int(actual)
        except:
            return False
    elif type(expected) == float:
        try:
            return expected == float(actual)
        except:
            return False
    elif type(expected) == bool:
        try:
            if actual.lower() in ['yes', 'true', 't', '1']:
                bool_val = True
            elif actual.lower() in ['no', 'false', 'f', '0']:
                bool_val = False
            else:
                raise Exception('Expected one of: [yes, no, true, false, t, f, 1, 0]. Got %s instead' % actual)
            return expected == bool_val
        except:
            return False
    else:
        return '{}'.format(expected) == '{}'.format(actual)


def identify_missing_xlvals(expected_xl_values, configfile):
    """
    Compare the expected values to what's been read from the config file.
    Will work with:
    - values.xlvals
    - secrets.xlvals
    """
    missing_values = {}
    for ek, ev in expected_xl_values.items():
        match = True
        val = None
        if configfile.has_option('default', ek):
            val = configfile.get('default', ek)
            if not type_aware_equals(ev, val):
                match = False
        else:
            match = False

        if not match:
            if val is None:
                missing_values[ek] = {'expected': ev}
            else:
                missing_values[ek] = {'expected': ev, 'actual': val}

    return missing_values

def run_tests(test_files, blueprint_dir, command_flags):
    env = os.environ.copy()
    env['PATH'] = '../:{}'.format(env['PATH'])

    for test_file in test_files:
        print('Processing blueprint test {}'.format(test_file))

        testdef = load_testdef_from_yaml_file(test_file)
        validate_testdef(testdef)

        answers_file = '{}/{}'.format(os.path.dirname(test_file), testdef['answers-file'])
        if not os.path.exists(answers_file):
            errormsg('Missing answers file {}'.format(answers_file))
            sys.exit(1)

        try:
            tempdir = tempfile.TemporaryDirectory(dir='.')
        except:
            errormsg('Unable to create temporary directory. Aborting')
            sys.exit(1)

        os.chdir(tempdir.name)
        
        command = ['../xl'] + command_flags + ['--blueprint', '{}'.format(blueprint_dir), '--answers', '../{}'.format(answers_file)]

        print('Executing: {}'.format(' '.join(command)))
        try:
            result = subprocess.run(command, capture_output=True, env=env)
        except Exception as err:
            errormsg('Tests failed with {0}'.format(err))
            sys.exit(1)
        if result.returncode != 0:
            if result.stdout:
                print('stdout: {}'.format(result.stdout))
            errormsg('Test failed on {} with message "{}"'.format(answers_file, result.stderr.decode('utf8').strip()))
            print(redtext('FAILED'))
            os.chdir('..')
            sys.exit(result.returncode)
        else:
            print(greentext('EXECUTION SUCCESS'))

        missing_files = []
        if 'expected-files' in testdef:
            if type(testdef['expected-files']) != list:
                errormsg('Expected a list for [expected-files], but got a {}'.format(type(testdef['expected-files'])))
                sys.exit(1)
            missing_files = identify_missing_files(testdef['expected-files'])
        unexpected_files = []
        if 'not-expected-files' in testdef:
            if type(testdef['not-expected-files']) != list:
                errormsg('Expected a list for [not-expected-files], but got a {}'.format(type(testdef['not-expected-files'])))
                sys.exit(1)
            unexpected_files = identify_not_missing_files(testdef['not-expected-files'])
        missing_xl_values = []
        if 'expected-xl-values' in testdef:
            if type(testdef['expected-xl-values']) != dict:
                errormsg('Expected a dict for [expected-xl-values], but got a {}'.format(type(testdef['expected-xl-values'])))
                sys.exit(1)
            configfile = parse_xlvals_file('xebialabs/values.xlvals')
            missing_xl_values = identify_missing_xlvals(testdef['expected-xl-values'], configfile)
        missing_xl_secrets = []
        if 'expected-xl-secrets' in testdef:
            if type(testdef['expected-xl-secrets']) != dict:
                errormsg('Expected a dict for [expected-xl-secrets], but got a {}'.format(type(testdef['expected-xl-secrets'])))
                sys.exit(1)
            configfile = parse_xlvals_file('xebialabs/secrets.xlvals')
            missing_xl_secrets = identify_missing_xlvals(testdef['expected-xl-secrets'], configfile)

        os.chdir('..')
        try:
            tempdir.cleanup()
        except:
            errormsg('Could not remove temp directory')
            sys.exit(1)

        test_passed = True
        if missing_files:
            for missing_file in missing_files:
                errormsg('Could not find expected file {}'.format(missing_file))
            test_passed = False

        if unexpected_files:
            for unexpected_file in unexpected_files:
                errormsg('Found file that is not supposed to exist: {}'.format(unexpected_file))
            test_passed = False

        if missing_xl_values:
            for mk, mv in missing_xl_values.items():
                if 'actual' in mv:
                    errormsg("Could not find expected value in values.xlvals ({}) - expected '{}', got '{}'".format(mk, mv['expected'], mv['actual']))
                else:
                    errormsg("Could not find expected value in values.xlvals ({}) - expected '{}', but the entry is not in the file".format(mk, mv['expected']))
            test_passed = False

        if missing_xl_secrets:
            for mk, mv in missing_xl_secrets.items():
                if 'actual' in mv:
                    errormsg("Could not find expected value in secrets.xlvals ({}) - expected '{}', got '{}'".format(mk, mv['expected'], mv['actual']))
                else:
                    errormsg("Could not find expected value in secrets.xlvals ({}) - expected '{}', but the entry is not in the file".format(mk, mv['expected']))
            test_passed = False

        if test_passed:
            print(greentext('SUCCESS'))
            print('')
        else:
            print(redtext('FAILED'))
            sys.exit(1)

if __name__ == '__main__':
    # xl up tests
    test_dir = 'integration-tests'
    blueprint_dir = 'xl-infra'
    # Filter out new test files (containg v2 or new_files)
    test_files = filter(lambda x: 'v2' not in x and 'new_files' not in x, [filename for filename in glob.iglob('{}/**/test*.yaml'.format(test_dir), recursive=True)])
    if not test_files:
        errormsg('Missing test files under {}'.format(test_dir))
        sys.exit(1)
    print('')
    print(greentext('Executing unit tests for XL-UP'))
    print('')
    run_tests(test_files, blueprint_dir, ['up', '--quick-setup', '--dry-run', '--skip-k8s', '--skip-prompts', '--local-repo', '../'])

    # Blueprint tests
    blueprint_dirs = [blueprint_dir, 'xl-up']

    blueprint_to_test_dirs = {}
    for blueprint_dir in blueprint_dirs:
        blueprint_to_test_dirs[blueprint_dir] = '{}/__test__'.format(blueprint_dir)

    for blueprint_dir, test_dir in blueprint_to_test_dirs.items():
        print(greentext('Executing unit tests for Blueprint "{}"'.format(blueprint_dir)))
        print('')
        test_files = [filename for filename in glob.iglob('{}/**/test*.yaml'.format(test_dir), recursive=True)]
        if test_files:
            run_tests(test_files, blueprint_dir, ['blueprint', '--use-defaults', '--strict-answers', '--local-repo', '../'])
