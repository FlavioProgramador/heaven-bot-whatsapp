from django.core.exceptions import ValidationError
from django.test import TestCase

from institution.models import InstitutionSettings


class InstitutionSettingsTests(TestCase):
    def test_settings_can_store_official_location_data(self):
        config = InstitutionSettings.objects.create(name="Heaven", address="Endereço cadastrado pela equipe")
        self.assertEqual(config.address, "Endereço cadastrado pela equipe")

    def test_only_one_configuration_is_allowed(self):
        InstitutionSettings.objects.create(name="Heaven")
        second = InstitutionSettings(name="Outro")
        with self.assertRaises(ValidationError):
            second.full_clean()
