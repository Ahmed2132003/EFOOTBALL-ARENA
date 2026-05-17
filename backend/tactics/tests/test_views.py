"""
eFootball Arena — Tactics View Tests
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tactics.models import (
    CounterTactic,
    Formation,
    MetaTracker,
    PlayerPosition,
    TacticCard,
)


def make_formation(**kwargs):
    defaults = dict(
        play_style="balanced",
        difficulty_level="intermediate",
        attacking_rating=5,
        defensive_rating=5,
        possession_rating=5,
        pressing_rating=5,
        width_rating=5,
        tempo_rating=5,
        is_meta=False,
    )
    defaults.update(kwargs)
    return Formation.objects.create(**defaults)


class FormationListViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("tactics:formation-list")
        self.f1 = make_formation(name="4-3-3-v", code="4-3-3-v", play_style="possession", difficulty_level="intermediate", is_meta=True)
        self.f2 = make_formation(name="4-2-1-3-v", code="4-2-1-3-v", play_style="tiki_taka", difficulty_level="advanced", is_meta=True)
        self.f3 = make_formation(name="4-4-2-v", code="4-4-2-v", play_style="balanced", difficulty_level="beginner", is_meta=False)

    def test_list_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_paginated_response(self):
        response = self.client.get(self.url)
        self.assertIn("pagination", response.data)
        self.assertIn("results", response.data)

    def test_filter_by_difficulty_level(self):
        response = self.client.get(self.url, {"difficulty_level": "advanced"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertEqual(item["difficulty_level"], "advanced")

    def test_filter_by_play_style(self):
        response = self.client.get(self.url, {"play_style": "possession"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertEqual(item["play_style"], "possession")

    def test_filter_by_is_meta(self):
        response = self.client.get(self.url, {"is_meta": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertTrue(item["is_meta"])

    def test_search_by_name(self):
        response = self.client.get(self.url, {"search": "4-3-3-v"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertIn("4-3-3-v", names)

    def test_ordering_by_name(self):
        response = self.client.get(self.url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, sorted(names))

    def test_pagination_page_size(self):
        response = self.client.get(self.url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]), 2)

    def test_no_nested_relations_in_list(self):
        response = self.client.get(self.url)
        for item in response.data["results"]:
            self.assertNotIn("positions", item)
            self.assertNotIn("tactic_cards", item)


class FormationDetailViewTest(APITestCase):
    def setUp(self):
        self.formation = make_formation(name="4-2-3-1-v", code="4-2-3-1-v")
        PlayerPosition.objects.create(
            formation=self.formation,
            position_name="Goalkeeper",
            short_name="GK",
            x_coordinate=50.0,
            y_coordinate=5.0,
            tactical_role="GK",
            display_order=1,
        )
        TacticCard.objects.create(
            formation=self.formation,
            title="Test Guide",
            content="Content",
            strengths="Strengths",
            weaknesses="Weaknesses",
            use_when="Use when",
            avoid_when="Avoid when",
        )
        MetaTracker.objects.create(
            formation=self.formation,
            usage_count=500,
            win_rate=55.0,
            popularity_rank=2,
        )
        self.url = reverse("tactics:formation-detail", kwargs={"pk": self.formation.pk})

    def test_detail_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_has_positions(self):
        response = self.client.get(self.url)
        self.assertIn("positions", response.data)
        self.assertEqual(len(response.data["positions"]), 1)

    def test_detail_has_tactic_cards(self):
        response = self.client.get(self.url)
        self.assertIn("tactic_cards", response.data)
        self.assertEqual(len(response.data["tactic_cards"]), 1)

    def test_detail_has_meta_tracker(self):
        response = self.client.get(self.url)
        self.assertIn("meta_tracker", response.data)
        self.assertIsNotNone(response.data["meta_tracker"])

    def test_detail_404_for_nonexistent(self):
        url = reverse("tactics:formation-detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CounterFinderViewTest(APITestCase):
    def setUp(self):
        self.f1 = make_formation(name="4-3-3-c", code="4-3-3-c")
        self.f2 = make_formation(name="4-2-1-3-c", code="4-2-1-3-c")
        CounterTactic.objects.create(
            formation=self.f1,
            countered_by=self.f2,
            explanation="Test explanation",
            effectiveness_rating=8,
        )
        self.url = reverse("tactics:counter-finder", kwargs={"pk": self.f1.pk})

    def test_counter_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_counter_returns_formation_info(self):
        response = self.client.get(self.url)
        self.assertIn("formation", response.data)
        self.assertEqual(response.data["formation"]["id"], self.f1.pk)

    def test_counter_returns_best_counters(self):
        response = self.client.get(self.url)
        self.assertIn("best_counters", response.data)
        self.assertEqual(len(response.data["best_counters"]), 1)

    def test_counter_returns_counters_found(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["counters_found"], 1)

    def test_counter_404_for_nonexistent_formation(self):
        url = reverse("tactics:counter-finder", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_counter_empty_for_no_counters(self):
        f3 = make_formation(name="5-3-2-c", code="5-3-2-c")
        url = reverse("tactics:counter-finder", kwargs={"pk": f3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["counters_found"], 0)
        self.assertEqual(len(response.data["best_counters"]), 0)


class MetaTrackerViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("tactics:meta-tracker")
        for i, (name, rank, wr) in enumerate([
            ("4-3-3-m", 1, 60.0),
            ("4-2-1-3-m", 2, 55.0),
            ("4-2-3-1-m", 3, 50.0),
        ]):
            f = make_formation(name=name, code=name, is_meta=(i < 2))
            MetaTracker.objects.create(
                formation=f,
                usage_count=1000 - i * 100,
                win_rate=wr,
                popularity_rank=rank,
            )

    def test_meta_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_meta_returns_paginated_response(self):
        response = self.client.get(self.url)
        self.assertIn("results", response.data)

    def test_meta_has_rank_field(self):
        response = self.client.get(self.url)
        for item in response.data["results"]:
            self.assertIn("rank", item)

    def test_meta_has_formation_info(self):
        response = self.client.get(self.url)
        for item in response.data["results"]:
            self.assertIn("formation", item)
            self.assertIn("name", item["formation"])

    def test_meta_has_analytics(self):
        response = self.client.get(self.url)
        for item in response.data["results"]:
            self.assertIn("analytics", item)
            self.assertIn("win_rate", item["analytics"])