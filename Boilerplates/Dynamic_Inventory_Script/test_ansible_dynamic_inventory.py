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
        self.inventory.add_hosts(hosts=['host1', 'host2'], group='group1', vars={'var1': 'value1'}, group_vars={'group_var1': 'value1'})
        self.assertIn('host1', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host2', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host1', self.inventory.inventory['group1']['hosts'])
        self.assertIn('host2', self.inventory.inventory['group1']['hosts'])
        self.assertEqual(self.inventory.inventory['group1']['vars']['group_var1'], 'value1')

    def test_add_host_to_group(self):
        self.inventory.add_host(host='host1', group=None)
        self.inventory.add_host_to_group(host='host1', group='group1', vars={'var1': 'value1'}, group_vars={'group_var1': 'value1'})
        self.assertIn('host1', self.inventory.inventory['_meta']['hostvars'])
        self.assertIn('host1', self.inventory.inventory['group1']['hosts'])
        self.assertEqual(self.inventory.inventory['group1']['vars']['group_var1'], 'value1')
        self.assertNotIn('host1', self.inventory.inventory['ungrouped']['hosts'])

    def test_add_child_group(self):
        self.inventory.add_child_group(parent_group='group1', child_group='child_group1', group_vars={'var1': 'value1'})
        self.assertIn('child_group1', self.inventory.inventory['group1']['children'])
        self.assertEqual(self.inventory.inventory['child_group1']['vars']['var1'], 'value1')

    def test_add_group(self):
        self.inventory.add_group(group='group1', group_vars={'var1': 'value1'})
        self.assertIn('group1', self.inventory.inventory['all']['children'])
        self.assertIn('vars', self.inventory.inventory['group1'])
        self.assertEqual(self.inventory.inventory['group1']['vars']['var1'], 'value1')

    def test_add_group_vars(self):
        self.inventory.add_group_vars(group='group1', group_vars={'var1': 'value1'})
        self.assertIn('vars', self.inventory.inventory['group1'])
        self.assertEqual(self.inventory.inventory['group1']['vars']['var1'], 'value1')

    def test_get_hosts(self):
        self.inventory.add_host(host='host1', vars={'var1': 'value1'})
        hosts = self.inventory.get_hosts()
        self.assertIn('host1', hosts)
        self.assertEqual(hosts['host1']['var1'], 'value1')

    def test_get_groups(self):
        self.inventory.add_host(host='host1', group='group1', vars={'var1': 'value1'})
        groups = self.inventory.get_groups()
        self.assertIn('group1', groups)
        self.assertIn('vars', groups['group1'])

    def test_get_child_groups(self):
        self.inventory.add_child_group(parent_group='group1', child_group='child_group1')
        child_groups = self.inventory.get_child_groups('group1')
        self.assertIn('child_group1', child_groups)

    def test_get_host(self):
        self.inventory.add_host(host='host1', vars={'var1': 'value1'})
        host_vars = self.inventory.get_host('host1')
        self.assertIsNotNone(host_vars)
        self.assertEqual(host_vars['var1'], 'value1')

    def test_get_group(self):
        self.inventory.add_group(group='group1', group_vars={'var1': 'value1'})
        group_vars = self.inventory.get_group('group1')
        self.assertIsNotNone(group_vars)
        self.assertEqual(group_vars['var1'], 'value1')


if __name__ == '__main__':
    unittest.main()
