import unittest
from dynamic_inventory_script import AnsibleDynamicInventory


class TestAnsibleDynamicInventory(unittest.TestCase):
    def setUp(self):
        self.inventory = AnsibleDynamicInventory()

    def test_add_host(self):
        self.inventory.add_host('group1', 'host1', {'var1': 'value1'})
        self.assertIn('host1', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host1', self.inventory.inventory['group1']['hosts'])
        self.assertEqual(self.inventory.inventory['_meta']['hostvars']['host1']['var1'], 'value1')

    def test_add_hosts(self):
        self.inventory.add_hosts('group1', ['host1', 'host2'], {'var1': 'value1'})
        self.assertIn('host1', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host2', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host1', self.inventory.inventory['group1']['hosts'])
        self.assertIn('host2', self.inventory.inventory['group1']['hosts'])

    def test_add_host_to_group(self):
        self.inventory.add_host_to_group('group1', 'host1', {'var1': 'value1'})
        self.assertIn('host1', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host1', self.inventory.inventory['group1']['hosts'])

    def test_add_child_group(self):
        self.inventory.add_child_group('group1', 'child_group1')
        self.assertIn('child_group1', self.inventory.inventory['group1']['children'])


if __name__ == '__main__':
    unittest.main()
