from django.test import TestCase

from operators.scripts.utils import CoordTransformer


class UtilsTest(TestCase):
    def test_lambert(self):
        transformer = CoordTransformer()

        first_input = [700000, 6600000]
        first_result = transformer.transform(first_input[0], first_input[1])
        first_expected = (46.50000000000001, 3.0000000000000004)
        self.assertEqual(first_result, first_expected)

        first_input = [0, 3]
        first_result = transformer.transform(first_input[0], first_input[1])
        first_expected = (-5.983837626281218, -1.3630822422782436)
        self.assertEqual(first_result, first_expected)
