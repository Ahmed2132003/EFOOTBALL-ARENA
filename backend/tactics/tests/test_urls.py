"""
eFootball Arena — Tactics URL Tests
"""

from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TacticsURLsTest(SimpleTestCase):
    def test_formation_list_url_resolves(self):
        url = reverse("tactics:formation-list")
        self.assertEqual(url, "/api/v1/tactics/formations/")

    def test_formation_detail_url_resolves(self):
        url = reverse("tactics:formation-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/v1/tactics/formations/1/")

    def test_counter_finder_url_resolves(self):
        url = reverse("tactics:counter-finder", kwargs={"pk": 1})
        self.assertEqual(url, "/api/v1/tactics/counter/1/")

    def test_meta_tracker_url_resolves(self):
        url = reverse("tactics:meta-tracker")
        self.assertEqual(url, "/api/v1/tactics/meta/")

    def test_formation_list_resolves_to_view(self):
        resolver = resolve("/api/v1/tactics/formations/")
        self.assertEqual(resolver.view_name, "tactics:formation-list")

    def test_formation_detail_resolves_to_view(self):
        resolver = resolve("/api/v1/tactics/formations/5/")
        self.assertEqual(resolver.view_name, "tactics:formation-detail")
        self.assertEqual(resolver.kwargs["pk"], 5)