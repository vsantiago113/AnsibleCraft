#!/usr/bin/env python3

import argparse
import json
from typing import List, Dict, Optional


class AnsibleDynamicInventory:
    def __init__(self):
        self.inventory = {
            '_meta': {
                'hostvars': {}
            },
            'all': {
                'children': [
                    'ungrouped'
                ]
            },
            'ungrouped': {
                'hosts': [],
                'vars': {}
            }
        }

    def __getitem__(self, item):
        return self.inventory[item]

    def add_hosts(
            self, *, hosts: Optional[List[str]] = None, group: str, vars: Optional[Dict] = None,
            group_vars: Optional[Dict] = None
            ) -> None:
        """
        Add multiple hosts to a group with optional host and group variables.

        Args:
            group (str): The group to add the hosts to.
            hosts (List[str], optional): A list of host IPs or names.
            vars (Dict, optional): A dictionary of variables to associate with the hosts.
            group_vars (Dict, optional): A dictionary of variables to associate with the group.
        """
        hosts = hosts or []
        vars = vars or {}
        group_vars = group_vars or {}

        self._ensure_group_exists(group=group, group_vars=group_vars)

        for host in hosts:
            self.add_host(host=host, group=group, vars=vars)

    def add_host(
            self, *, host: str, group: Optional[str], vars: Optional[Dict] = None, group_vars: Optional[Dict] = None
            ) -> None:
        """
        Add a single host to a group with optional host and group variables.

        Args:
            group (str): The group to add the host to.
            host (str): The host IP or name.
            vars (Dict, optional): A dictionary of variables to associate with the host.
            group_vars (Dict, optional): A dictionary of variables to associate with the group.
        """
        vars = vars or {}
        group_vars = group_vars or {}

        self.inventory['_meta']['hostvars'].setdefault(host, {}).update(vars)

        if group:
            self._ensure_group_exists(group=group, group_vars=group_vars)
            if host not in self.inventory[group]['hosts']:
                self.inventory[group]['hosts'].append(host)
        else:
            if host not in self.inventory['ungrouped']['hosts']:
                self.inventory['ungrouped']['hosts'].append(host)

    def add_host_to_group(
            self, *, host: str, group: str, vars: Optional[Dict] = None, group_vars: Optional[Dict] = None
            ) -> None:
        """
        Add an existing host to a group, or create and add the host if it doesn't exist,
        with optional host and group variables.

        Args:
            group (str): The group to add the host to.
            host (str): The host IP or name.
            vars (Dict, optional): A dictionary of variables to associate with the host.
            group_vars (Dict, optional): A dictionary of variables to associate with the group.
        """
        self.add_host(host=host, group=group, vars=vars, group_vars=group_vars)

    def add_child_group(self, *, parent_group: str, child_group: str, group_vars: Optional[Dict] = None) -> None:
        """
        Add a child group to an existing group with optional variables.

        Args:
            parent_group (str): The parent group to add the child group to.
            child_group (str): The child group to add.
            group_vars (Dict, optional): A dictionary of variables to associate with the child group.
        """
        self._ensure_group_exists(group=parent_group)
        self._ensure_group_exists(group=child_group, group_vars=group_vars)

        if 'children' not in self.inventory[parent_group]:
            self.inventory[parent_group]['children'] = []
        if child_group not in self.inventory[parent_group]['children']:
            self.inventory[parent_group]['children'].append(child_group)

    def _ensure_group_exists(self, *, group: str, group_vars: Optional[Dict] = None) -> None:
        """
        Ensure that a group exists in the 'all' children list, with optional variables.

        Args:
            group (str): The group to ensure existence of.
            group_vars (Dict, optional): A dictionary of variables to associate with the group.
        """
        if group not in self.inventory['all']['children']:
            self.inventory['all']['children'].append(group)
        if group not in self.inventory:
            self.inventory[group] = {'hosts': [], 'vars': {}, 'children': []}

        if group_vars:
            self.add_group_vars(group=group, group_vars=group_vars)

    def add_group_vars(self, *, group: str, group_vars: Dict) -> None:
        """
        Add variables to a group.

        Args:
            group (str): The group to add the variables to.
            group_vars (Dict): A dictionary of variables to associate with the group.
        """
        self._ensure_group_exists(group=group)
        self.inventory[group]['vars'].update(group_vars)

    def get_devices(self) -> Dict[str, Dict]:
        """
        Retrieve the devices from '_meta -> hostvars'.

        Returns:
            Dict[str, Dict]: A dictionary of devices and their variables.
        """
        return self.inventory['_meta']['hostvars']

    def get_groups(self) -> Dict[str, Dict]:
        """
        Retrieve the groups excluding '_meta'.

        Returns:
            Dict[str, Dict]: A dictionary of groups and their details.
        """
        return {k: v for k, v in self.inventory.items() if k != '_meta'}

    def get_child_groups(self, group: str) -> List[str]:
        """
        Retrieve the child groups of a specified group.

        Args:
            group (str): The group to retrieve child groups from.

        Returns:
            List[str]: A list of child groups.
        """
        if group in self.inventory:
            return self.inventory[group].get('children', [])
        return []


def main():
    parser = argparse.ArgumentParser(
        description='Command line arguments for Ansible Dynamic Inventory.')
    parser.add_argument(
        '--list', action='store_true', help='Return list of hosts.')
    parser.add_argument('--host', type=str, help='Return the requested host.')
    args = parser.parse_args()

    example_inventory = AnsibleDynamicInventory()

    # Example of adding multiple hosts to a group with variables
    example_inventory.add_hosts(
        hosts=['host1'], group='group1',
        vars={
            'ansible_host': '192.168.1.10',
            'ansible_user': 'user1',
            'ansible_ssh_private_key_file': '/path/to/private/key'
        },
        group_vars={
            'group_var1': 'value1',
            'group_var2': 'value2'
        }
    )
    example_inventory.add_hosts(
        hosts=['host2'], group='group2',
        vars={
            'ansible_host': '192.168.1.11',
            'ansible_user': 'user2',
            'ansible_ssh_private_key_file': '/path/to/private/key'
        }
    )

    # Example of adding a single host to the 'ungrouped' group
    example_inventory.add_host(
        host='host3', group=None, vars={
            'ansible_host': '192.168.1.12',
            'ansible_user': 'user3',
            'ansible_ssh_private_key_file': '/path/to/private/key'
        }
    )

    # Example of adding an existing host to another group
    example_inventory.add_host_to_group(host='host1', group='group2')

    # Example of adding a child group to a group with variables
    example_inventory.add_child_group(
        parent_group='group1', child_group='child_group1',
        group_vars={
            'var1': 'value1',
            'var2': 'value2'
        }
    )

    if args.list:
        print(json.dumps(example_inventory.inventory, indent=4))
    elif args.host:
        print(json.dumps(
            example_inventory.inventory['_meta']['hostvars'].get(
                args.host, {}
            ), indent=4
        ))

    # Loop through devices
    print("Devices:")
    for device in example_inventory.get_devices():
        print(device)

    # Loop through groups
    print("\nGroups:")
    for group in example_inventory.get_groups():
        print(group)

    # Loop through child groups of 'group1'
    print("\nChild groups of 'group1':")
    for child_group in example_inventory.get_child_groups('group1'):
        print(child_group)


if __name__ == '__main__':
    main()
