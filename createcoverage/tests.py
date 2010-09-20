import os
import shutil
import sys
import tempfile
import webbrowser
from unittest import TestCase

from createcoverage import script


executed = []

def mock_sys_exit(exit_code):
    raise RuntimeError("MOCK sys.exit(%s)" % exit_code)


def mock_webbrowser_open(path):
    global executed
    executed.append("Opened %s in webbrowser" % path)


def mock_system(command):
    global executed
    executed.append("Executed %s" % command)


class TestSystemCommand(TestCase):

    def setUp(self):
        self.orig_exit = sys.exit
        sys.exit = mock_sys_exit

    def tearDown(self):
        sys.exit = self.orig_exit

    def test_correct_command(self):
        script.system("dir")

    def test_failing_command(self):
        self.assertRaises(RuntimeError, script.system, "non_existing_command")


class TestCoverage(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.orig_dir = os.getcwd()
        self.orig_webbrowser_open = webbrowser.open
        webbrowser.open = mock_webbrowser_open
        self.orig_system = script.system
        script.system = mock_system
        os.chdir(self.tempdir)
        global executed
        executed = []

    def tearDown(self):
        webbrowser.open = self.orig_webbrowser_open
        script.system = self.orig_system
        os.chdir(self.orig_dir)
        shutil.rmtree(self.tempdir)

    def test_missing_bin_test(self):
        self.assertRaises(RuntimeError, script.main)

    def test_missing_bin_coverage(self):
        bindir = os.path.join(self.tempdir, 'bin')
        testbinary = os.path.join(bindir, 'test')
        os.mkdir(bindir)
        open(testbinary, 'w').write('hello')
        self.assertRaises(RuntimeError, script.main)

    def test_normal_run(self):
        bindir = os.path.join(self.tempdir, 'bin')
        testbinary = os.path.join(bindir, 'test')
        coveragebinary = os.path.join(bindir, 'coverage')
        os.mkdir(bindir)
        open(testbinary, 'w').write('hello')
        open(coveragebinary, 'w').write('hello')
        script.main()
        self.assertTrue('bin/coverage run' in executed[0])
        self.assertTrue('bin/coverage html' in executed[1])
        self.assertTrue('Opened' in executed[2])
        script.main()
