import unittest
from dynamic_inventory_script import AnsibleDynamicInventory


class TestAnsibleDynamicInventory(unittest.TestCase):
    def setUp(self):
        self.inventory = AnsibleDynamicInventory()

    def test_add_host(self):
        self.inventory.add_host(host='host1', group='group1', vars={'var1': 'value1'}, group_vars={'group_var1': 'value1'})
        self.assertIn('host1', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host1', self.inventory.inventory['group1']['hosts'])
        self.assertEqual(self.inventory.inventory['_meta']['hostvars']['host1']['var1'], 'value1')
        self.assertEqual(self.inventory.inventory['group1']['vars']['group_var1'], 'value1')

    def test_add_hosts(self):
        self.inventory.add_hosts(
            hosts=['host1', 'host2'], group='group1', vars={'var1': 'value1'}, group_vars={'group_var1': 'value1'}
            )
        self.assertIn('host1', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host2', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host1', self.inventory.inventory['group1']['hosts'])
        self.assertIn('host2', self.inventory.inventory['group1']['hosts'])
        self.assertEqual(self.inventory.inventory['group1']['vars']['group_var1'], 'value1')

    def test_add_host_to_group(self):
        self.inventory.add_host_to_group(
            host='host1', group='group1', vars={'var1': 'value1'}, group_vars={'group_var1': 'value1'}
            )
        self.assertIn('host1', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host1', self.inventory.inventory['group1']['hosts'])
        self.assertEqual(self.inventory.inventory['group1']['vars']['group_var1'], 'value1')

    def test_add_child_group(self):
        self.inventory.add_child_group(parent_group='group1', child_group='child_group1', group_vars={'var1': 'value1'})
        self.assertIn('child_group1', self.inventory.inventory['group1']['children'])
        self.assertEqual(self.inventory.inventory['child_group1']['vars']['var1'], 'value1')

    def test_ensure_group_exists(self):
        self.inventory._ensure_group_exists(group='group1', group_vars={'var1': 'value1'})
        self.assertIn('group1', self.inventory.inventory['all']['children'])
        self.assertEqual(self.inventory.inventory['group1']['vars']['var1'], 'value1')

    def test_add_group_vars(self):
        self.inventory.add_group_vars(group='group1', group_vars={'var1': 'value1'})
        self.assertEqual(self.inventory.inventory['group1']['vars']['var1'], 'value1')

    def test_get_devices(self):
        self.inventory.add_host(host='host1', group='group1', vars={'var1': 'value1'})
        devices = self.inventory.get_devices()
        self.assertIn('host1', devices)
        self.assertEqual(devices['host1']['var1'], 'value1')

    def test_get_groups(self):
        self.inventory.add_host(host='host1', group='group1', vars={'var1': 'value1'})
        groups = self.inventory.get_groups()
        self.assertIn('group1', groups)

    def test_get_child_groups(self):
        self.inventory.add_child_group(parent_group='group1', child_group='child_group1')
        child_groups = self.inventory.get_child_groups('group1')
        self.assertIn('child_group1', child_groups)


if __name__ == '__main__':
    unittest.main()
