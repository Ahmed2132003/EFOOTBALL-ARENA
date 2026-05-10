from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testplayer",
            email="test@arena.com",
            password="StrongPass123!",
            country="EG",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testplayer")
        self.assertEqual(self.user.email, "test@arena.com")
        self.assertTrue(self.user.check_password("StrongPass123!"))

    def test_default_rank_level(self):
        self.assertEqual(self.user.rank_level, "Bronze")

    def test_default_rating(self):
        self.assertEqual(self.user.rating, 1000.0)

    def test_default_is_verified(self):
        self.assertFalse(self.user.is_verified)

    def test_str_representation(self):
        self.assertEqual(str(self.user), "testplayer (Bronze)")

    def test_rank_level_choices(self):
        valid_ranks = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Legend"]
        for rank in valid_ranks:
            self.user.rank_level = rank
            self.user.save()
            self.user.refresh_from_db()
            self.assertEqual(self.user.rank_level, rank)