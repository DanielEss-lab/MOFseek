from unittest import TestCase

from MofIdentifier.SubGraphMatching import CustomWildcard


class TestWC(TestCase):
    def test_matches(self):

        self.fail()

    def test_parse_line(self):
        expected = [CustomWildcard.WC(), ]
        wildcards = CustomWildcard.WC.parse_line("Wc1=Cd,Ca,Fe;Wc2=notH")
        self.assertEqual(expected, wildcards)