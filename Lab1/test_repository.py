import unittest
from models import Vehicle
from repository import InMemoryVehicleRepository

class TestInMemoryVehicleRepository(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryVehicleRepository()
        self.test_vehicle = Vehicle(id=None, make="Volvo", model="FH16", license_plate="AA1111BB", year=2020)

    def test_create_and_read(self):
        created = self.repo.create(self.test_vehicle)
        self.assertIsNotNone(created.id)
        self.assertEqual(created.make, "Volvo")
        
        fetched = self.repo.get_by_id(created.id)
        self.assertEqual(fetched.license_plate, "AA1111BB")

    def test_update(self):
        created = self.repo.create(self.test_vehicle)
        created.make = "Scania"
        
        updated = self.repo.update(created)
        self.assertEqual(updated.make, "Scania")
        self.assertEqual(self.repo.get_by_id(created.id).make, "Scania")

    def test_delete(self):
        created = self.repo.create(self.test_vehicle)
        self.assertTrue(self.repo.delete(created.id))
        self.assertIsNone(self.repo.get_by_id(created.id))

    def test_pagination(self):
        for i in range(5):
            self.repo.create(Vehicle(id=None, make="Brand", model=f"Model {i}", license_plate=f"00{i}", year=2020))
        
        batch = self.repo.get_all(limit=2, offset=2)
        
        self.assertEqual(len(batch), 2)
        self.assertEqual(batch[0].model, "Model 2")
        self.assertEqual(batch[1].model, "Model 3")

if __name__ == '__main__':
    unittest.main()