"""Tests for the help subcommand"""
import os
from util_functions import SCRIPT_LOC, script_cmd


class TestHelp:
    """Test help subcommand functions"""
    def test_help(self, capfd):
        """Test if help text gets printed"""
        script_cmd(SCRIPT_LOC + ' --help', os.getcwd())
        out, err = capfd.readouterr()
        assert out.startswith('usage: ofStateManager.py [-h]')
        assert err == ''

    def test_help_record(self, capfd):
        """Test if record help text gets printed"""
        script_cmd(SCRIPT_LOC + ' record -h', os.getcwd())
        out, err = capfd.readouterr()
        assert out.startswith('usage: ofStateManager.py record [-h]')
        assert err == ''

    def test_help_checkout(self, capfd):
        """Test if checkout help text gets printed"""
        script_cmd(SCRIPT_LOC + ' checkout --help', os.getcwd())
        out, err = capfd.readouterr()
        assert out.startswith('usage: ofStateManager.py checkout [-h]')
        assert err == ''

    def test_help_archive(self, capfd):
        """Test if archive help text gets printed"""
        script_cmd(SCRIPT_LOC + ' archive -h', os.getcwd())
        out, err = capfd.readouterr()
        assert out.startswith('usage: ofStateManager.py archive [-h]')
        assert err == ''

    def test_help_list(self, capfd):
        """Test if list help text gets printed"""
        script_cmd(SCRIPT_LOC + ' list --help', os.getcwd())
        out, err = capfd.readouterr()
        assert out.startswith('usage: ofStateManager.py list [-h]')
        assert err == ''
