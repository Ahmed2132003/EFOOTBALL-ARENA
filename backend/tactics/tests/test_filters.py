"""
eFootball Arena — Tactics Filter Tests
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from tactics.models import Formation


def make_formation(**kwargs):
    defaults = dict(
        play_style="balanced",
        difficulty_level="intermediate",
        attacking_rating=5, defensive_rating=5,
        possession_rating=5, pressing_rating=5,
        width_rating=5, tempo_rating=5, is_meta=False,
    )
    defaults.update(kwargs)
    return Formation.objects.create(**defaults)


class FormationFilterTest(APITestCase):
    def setUp(self):
        self.url = reverse("tactics:formation-list")
        make_formation(name="F-beginner", code="F-b", difficulty_level="beginner", play_style="defensive", is_meta=False)
        make_formation(name="F-intermediate", code="F-i", difficulty_level="intermediate", play_style="possession", is_meta=True)
        make_formation(name="F-advanced", code="F-a", difficulty_level="advanced", play_style="tiki_taka", is_meta=True)

    def test_filter_beginner(self):
        res = self.client.get(self.url, {"difficulty_level": "beginner"})
        self.assertEqual(res.status_code, 200)
        for item in res.data["results"]:
            self.assertEqual(item["difficulty_level"], "beginner")

    def test_filter_meta_true(self):
        res = self.client.get(self.url, {"is_meta": "true"})
        for item in res.data["results"]:
            self.assertTrue(item["is_meta"])

    def test_filter_meta_false(self):
        res = self.client.get(self.url, {"is_meta": "false"})
        for item in res.data["results"]:
            self.assertFalse(item["is_meta"])

    def test_search_returns_correct_results(self):
        res = self.client.get(self.url, {"search": "F-beginner"})
        names = [i["name"] for i in res.data["results"]]
        self.assertIn("F-beginner", names)

    def test_ordering_by_attacking_rating_desc(self):
        make_formation(name="F-high-att", code="F-ha", attacking_rating=9)
        make_formation(name="F-low-att", code="F-la", attacking_rating=2)
        res = self.client.get(self.url, {"ordering": "-attacking_rating"})
        ratings = [i["attacking_rating"] for i in res.data["results"]]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_combined_filter_and_search(self):
        res = self.client.get(self.url, {"is_meta": "true", "search": "F-advanced"})
        names = [i["name"] for i in res.data["results"]]
        self.assertIn("F-advanced", names)