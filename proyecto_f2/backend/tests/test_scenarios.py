import unittest
from copy import deepcopy

from pydantic import ValidationError

from app.schemas.scenario import ScenarioConfiguration
from app.services.scenario_service import DEFAULT_CONFIGURATION


class ScenarioValidationTests(unittest.TestCase):
    def test_default_scenario_is_valid(self):
        scenario = ScenarioConfiguration.model_validate(DEFAULT_CONFIGURATION)
        self.assertEqual(scenario.map.width, 10)
        self.assertEqual(len(scenario.packages), 5)
        self.assertEqual(len(scenario.zones), 2)
        self.assertEqual(len(scenario.obstacles), 8)

    def test_rejects_package_over_an_obstacle(self):
        configuration = deepcopy(DEFAULT_CONFIGURATION)
        configuration["packages"][0]["x"] = configuration["obstacles"][0]["x"]
        configuration["packages"][0]["y"] = configuration["obstacles"][0]["y"]
        with self.assertRaises(ValidationError):
            ScenarioConfiguration.model_validate(configuration)

    def test_rejects_unknown_delivery_zone(self):
        configuration = deepcopy(DEFAULT_CONFIGURATION)
        configuration["packages"][0]["zone"] = "zona_inexistente"
        with self.assertRaises(ValidationError):
            ScenarioConfiguration.model_validate(configuration)

    def test_allows_custom_scenario_without_packages(self):
        configuration = deepcopy(DEFAULT_CONFIGURATION)
        configuration["packages"] = []
        scenario = ScenarioConfiguration.model_validate(configuration)
        self.assertEqual(scenario.packages, [])

    def test_allows_added_shelf_and_relocated_zone(self):
        configuration = deepcopy(DEFAULT_CONFIGURATION)
        configuration["zones"][0]["x"] = 4
        configuration["zones"][0]["y"] = 4
        configuration["obstacles"].append({"x": 1, "y": 2})
        scenario = ScenarioConfiguration.model_validate(configuration)
        self.assertEqual((scenario.zones[0].x, scenario.zones[0].y), (4, 4))
        self.assertEqual(len(scenario.obstacles), 9)


if __name__ == "__main__":
    unittest.main()
