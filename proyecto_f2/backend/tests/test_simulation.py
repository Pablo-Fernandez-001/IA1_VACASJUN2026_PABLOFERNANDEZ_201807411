import shutil
import unittest
from copy import deepcopy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.models.entities import Scenario, SimulationCheckpoint
from app.routers.simulation import history_detail
from app.services import simulation_service
from app.services.scenario_service import DEFAULT_CONFIGURATION


class SimulationConfigurationTests(unittest.TestCase):
    def tearDown(self):
        simulation_service.ACTIVE_CONFIGURATION = deepcopy(DEFAULT_CONFIGURATION)
        simulation_service.ACTIVE_SCENARIO = {
            "id": None,
            "name": "Bodega clasica",
            "is_default": True,
            "dirty": False,
        }
        simulation_service.STATE = simulation_service._runtime_from_configuration(
            DEFAULT_CONFIGURATION
        )

    def test_custom_package_position_survives_runtime_reset(self):
        custom = deepcopy(DEFAULT_CONFIGURATION)
        custom["packages"][0]["x"] = 2
        custom["packages"][0]["y"] = 2
        custom["obstacles"][0]["x"] = 4
        custom["obstacles"][0]["y"] = 4
        simulation_service.activate_configuration(custom, scenario_name="Prueba", dirty=True)
        simulation_service.reset_state()
        state = simulation_service.current_state()
        package = next(item for item in state["packages"] if item["id"] == "p1")
        self.assertEqual((package["x"], package["y"]), (2, 2))
        self.assertIn({"x": 4, "y": 4}, state["obstacles"])
        self.assertEqual(state["scenario"]["name"], "Prueba")

    def test_empty_inventory_completes_on_start(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        db = sessionmaker(bind=engine)()
        custom = deepcopy(DEFAULT_CONFIGURATION)
        custom["packages"] = []
        simulation_service.activate_configuration(custom, scenario_name="Sin paquetes")
        result = simulation_service.start(db)
        simulation_id = result["simulation_id"]
        self.assertIsNotNone(result["scenario"]["id"])
        self.assertTrue(result["scenario"]["name"].startswith("Auto "))
        self.assertEqual(db.query(Scenario).count(), 1)
        self.assertEqual(
            [item.event for item in db.query(SimulationCheckpoint).filter_by(simulation_id=simulation_id).all()],
            ["started", "completed"],
        )
        simulation_service.reset(db)
        events = [item.event for item in db.query(SimulationCheckpoint).filter_by(simulation_id=simulation_id).order_by(SimulationCheckpoint.id).all()]
        db.close()
        self.assertEqual(result["phase"], "completed")
        self.assertEqual(result["deliveries"], 0)
        self.assertEqual(events, ["started", "completed", "reset"])


@unittest.skipUnless(shutil.which("swipl"), "SWI-Prolog no esta disponible")
class PrologEndToEndTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        simulation_service.STATE = simulation_service._runtime_from_configuration(
            simulation_service.ACTIVE_CONFIGURATION
        )
        simulation_service.activate_configuration(
            DEFAULT_CONFIGURATION,
            scenario_name="Bodega de prueba",
        )

    def tearDown(self):
        self.db.close()
        simulation_service.reset_state()

    def test_prolog_completes_all_default_deliveries(self):
        simulation_service.start(self.db)
        for _ in range(250):
            result = simulation_service.step(self.db)
            if result["phase"] == "completed":
                break
            self.assertNotEqual(result["last_action"], "esperar")
        self.assertEqual(result["deliveries"], 5)
        self.assertEqual(result["phase"], "completed")
        self.assertEqual(result["last_source"], "prolog")
        detail = history_detail(result["simulation_id"], self.db)
        self.assertEqual(detail["analytics"]["deliveries"], 5)
        self.assertEqual(detail["analytics"]["waits"], 0)
        self.assertEqual(sum(detail["analytics"]["action_counts"].values()), result["steps"])
        self.assertEqual([item["event"] for item in detail["checkpoints"]], ["started", "completed"])


if __name__ == "__main__":
    unittest.main()
