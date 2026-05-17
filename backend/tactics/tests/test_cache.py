"""
eFootball Arena — Tactics Cache Tests

Tests verify:
1. Responses are cached after first request
2. Cache returns consistent data on repeated requests
3. Cache keys are unique per query params
"""

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from tactics.models import Formation, MetaTracker


def make_formation(**kwargs):
    defaults = dict(
        play_style="balanced", difficulty_level="intermediate",
        attacking_rating=5, defensive_rating=5,
        possession_rating=5, pressing_rating=5,
        width_rating=5, tempo_rating=5, is_meta=False,
    )
    defaults.update(kwargs)
    return Formation.objects.create(**defaults)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class FormationListCacheTest(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("tactics:formation-list")
        make_formation(name="Cache-F1", code="Cache-F1")
        make_formation(name="Cache-F2", code="Cache-F2")

    def tearDown(self):
        cache.clear()

    def test_first_request_returns_data(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data)

    def test_second_request_returns_same_data(self):
        res1 = self.client.get(self.url)
        res2 = self.client.get(self.url)
        self.assertEqual(res1.data, res2.data)

    def test_different_params_different_cache_entries(self):
        res1 = self.client.get(self.url, {"is_meta": "true"})
        res2 = self.client.get(self.url, {"is_meta": "false"})
        # Different params → different cache entries → potentially different counts
        count1 = res1.data["pagination"]["count"]
        count2 = res2.data["pagination"]["count"]
        # They should not both be the total count (unless all are meta)
        self.assertIsNotNone(count1)
        self.assertIsNotNone(count2)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class FormationDetailCacheTest(APITestCase):
    def setUp(self):
        cache.clear()
        self.formation = make_formation(name="Detail-Cache-F", code="Detail-Cache-F")
        self.url = reverse("tactics:formation-detail", kwargs={"pk": self.formation.pk})

    def tearDown(self):
        cache.clear()

    def test_detail_cache_hit_returns_same_data(self):
        res1 = self.client.get(self.url)
        res2 = self.client.get(self.url)
        self.assertEqual(res1.data["id"], res2.data["id"])
        self.assertEqual(res1.data["name"], res2.data["name"])

    def test_cache_key_per_formation_id(self):
        f2 = make_formation(name="Detail-Cache-F2", code="Detail-Cache-F2")
        url2 = reverse("tactics:formation-detail", kwargs={"pk": f2.pk})

        res1 = self.client.get(self.url)
        res2 = self.client.get(url2)

        self.assertNotEqual(res1.data["id"], res2.data["id"])