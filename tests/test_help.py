"""Tests for the help subcommand"""
from util_functions import run_ofSM


class TestHelp:
    """Test help subcommand functions"""
    def test_help(self, capfd):
        """Test if help text gets printed"""
        out, err = run_ofSM('--help', capfd=capfd)
        assert out.startswith('usage: ofStateManager.py [-h]')
        assert err == ''

    def test_help_record(self, capfd):
        """Test if record help text gets printed"""
        out, err = run_ofSM('record -h', capfd=capfd)
        assert out.startswith('usage: ofStateManager.py record [-h]')
        assert err == ''

    def test_help_checkout(self, capfd):
        """Test if checkout help text gets printed"""
        out, err = run_ofSM('checkout --help', capfd=capfd)
        assert out.startswith('usage: ofStateManager.py checkout [-h]')
        assert err == ''

    def test_help_archive(self, capfd):
        """Test if archive help text gets printed"""
        out, err = run_ofSM('archive -h', capfd=capfd)
        assert out.startswith('usage: ofStateManager.py archive [-h]')
        assert err == ''

    def test_help_list(self, capfd):
        """Test if list help text gets printed"""
        out, err = run_ofSM('list --help', capfd=capfd)
        assert out.startswith('usage: ofStateManager.py list [-h]')
        assert err == ''
