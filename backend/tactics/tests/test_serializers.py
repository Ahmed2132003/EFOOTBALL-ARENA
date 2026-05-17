"""
eFootball Arena — Tactics Serializer Tests
"""

import pytest
from django.test import TestCase

from tactics.models import Formation, MetaTracker, PlayerPosition, TacticCard
from tactics.serializers import (
    FormationDetailSerializer,
    FormationListSerializer,
    MetaTrackerSerializer,
    PlayerPositionSerializer,
    TacticCardSerializer,
)


class FormationListSerializerTest(TestCase):
    def setUp(self):
        self.formation = Formation.objects.create(
            name="4-3-3-test",
            code="4-3-3-test",
            play_style="possession",
            difficulty_level="intermediate",
            attacking_rating=8,
            defensive_rating=6,
            possession_rating=8,
            pressing_rating=7,
            width_rating=9,
            tempo_rating=7,
            is_meta=True,
        )

    def test_list_serializer_fields(self):
        serializer = FormationListSerializer(self.formation)
        data = serializer.data
        required_fields = [
            "id", "name", "code", "slug", "play_style", "difficulty_level",
            "attacking_rating", "defensive_rating", "possession_rating",
            "pressing_rating", "is_meta", "average_rating",
        ]
        for field in required_fields:
            self.assertIn(field, data)

    def test_average_rating_computed(self):
        serializer = FormationListSerializer(self.formation)
        avg = serializer.data["average_rating"]
        self.assertIsNotNone(avg)
        self.assertGreater(avg, 0)

    def test_no_nested_relations_in_list(self):
        """List serializer must NOT include positions or tactic_cards."""
        serializer = FormationListSerializer(self.formation)
        data = serializer.data
        self.assertNotIn("positions", data)
        self.assertNotIn("tactic_cards", data)
        self.assertNotIn("counter_tactics", data)


class FormationDetailSerializerTest(TestCase):
    def setUp(self):
        self.formation = Formation.objects.create(
            name="4-2-1-3-test",
            code="4-2-1-3-test",
            play_style="tiki_taka",
            difficulty_level="advanced",
            attacking_rating=9,
            defensive_rating=7,
            possession_rating=9,
            pressing_rating=6,
            width_rating=8,
            tempo_rating=8,
            is_meta=True,
        )
        self.position = PlayerPosition.objects.create(
            formation=self.formation,
            position_name="Goalkeeper",
            short_name="GK",
            x_coordinate=50.0,
            y_coordinate=5.0,
            tactical_role="GK",
            display_order=1,
        )
        self.tactic_card = TacticCard.objects.create(
            formation=self.formation,
            title="Test Guide",
            content="Test content",
            strengths="Test strengths",
            weaknesses="Test weaknesses",
            use_when="Test use_when",
            avoid_when="Test avoid_when",
        )
        MetaTracker.objects.create(
            formation=self.formation,
            usage_count=1000,
            win_rate=60.0,
            popularity_rank=1,
        )

    def test_detail_serializer_has_positions(self):
        formation = Formation.objects.prefetch_related(
            "positions", "tactic_cards", "is_countered_by__countered_by"
        ).select_related("meta_tracker").get(pk=self.formation.pk)
        serializer = FormationDetailSerializer(formation)
        self.assertIn("positions", serializer.data)
        self.assertEqual(len(serializer.data["positions"]), 1)

    def test_detail_serializer_has_tactic_cards(self):
        formation = Formation.objects.prefetch_related(
            "positions", "tactic_cards", "is_countered_by__countered_by"
        ).select_related("meta_tracker").get(pk=self.formation.pk)
        serializer = FormationDetailSerializer(formation)
        self.assertIn("tactic_cards", serializer.data)
        self.assertEqual(len(serializer.data["tactic_cards"]), 1)

    def test_detail_serializer_has_meta_tracker(self):
        formation = Formation.objects.prefetch_related(
            "positions", "tactic_cards", "is_countered_by__countered_by"
        ).select_related("meta_tracker").get(pk=self.formation.pk)
        serializer = FormationDetailSerializer(formation)
        self.assertIn("meta_tracker", serializer.data)
        self.assertIsNotNone(serializer.data["meta_tracker"])


class PlayerPositionSerializerTest(TestCase):
    def setUp(self):
        self.formation = Formation.objects.create(
            name="4-4-2-test", code="4-4-2-test"
        )
        self.position = PlayerPosition.objects.create(
            formation=self.formation,
            position_name="Goalkeeper",
            short_name="GK",
            x_coordinate=50.0,
            y_coordinate=5.0,
            tactical_role="GK",
            display_order=1,
        )

    def test_position_serializer_fields(self):
        serializer = PlayerPositionSerializer(self.position)
        data = serializer.data
        self.assertIn("x_coordinate", data)
        self.assertIn("y_coordinate", data)
        self.assertIn("short_name", data)
        self.assertIn("tactical_role", data)
        self.assertIn("display_order", data)

    def test_coordinates_are_floats(self):
        serializer = PlayerPositionSerializer(self.position)
        self.assertIsInstance(serializer.data["x_coordinate"], float)
        self.assertIsInstance(serializer.data["y_coordinate"], float)