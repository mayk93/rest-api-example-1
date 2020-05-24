from django.test import TestCase
from app.calc import add, substract


class CalcTests(TestCase):
    def test_add(self):
        self.assertEqual(add(2, 8), 10)

    def test_substract(self):
        self.assertEqual(substract(10, 5), 5)
