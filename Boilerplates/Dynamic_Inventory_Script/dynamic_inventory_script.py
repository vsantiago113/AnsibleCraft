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
                'vars': {},
                'children': []
            }
        }

    def __getitem__(self, item):
        return self.inventory[item]

    def add_group(self, *, group: str, group_vars: Optional[Dict] = None) -> None:
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

    def add_hosts(
            self, *, hosts: Optional[List[str]] = None, group: Optional[str] = None,
            vars: Optional[Dict] = None, group_vars: Optional[Dict] = None
            ) -> None:
        """
        Add multiple hosts to a group with optional host and group variables.

        Args:
            hosts (List[str], optional): A list of host IPs or names.
            group (str, optional): The group to add the hosts to.
            vars (Dict, optional): A dictionary of variables to associate with the hosts.
            group_vars (Dict, optional): A dictionary of variables to associate with the group.
        """
        hosts = hosts or []
        vars = vars or {}
        group_vars = group_vars or {}

        if group:
            self.add_group(group=group, group_vars=group_vars)

        for host in hosts:
            self.add_host(host=host, group=group, vars=vars)

    def add_host(
            self, *, host: str, group: Optional[str] = None, vars: Optional[Dict] = None,
            group_vars: Optional[Dict] = None
            ) -> None:
        """
        Add a single host to a group with optional host and group variables.

        Args:
            host (str): The host IP or name.
            group (str, optional): The group to add the host to.
            vars (Dict, optional): A dictionary of variables to associate with the host.
            group_vars (Dict, optional): A dictionary of variables to associate with the group.
        """
        vars = vars or {}
        group_vars = group_vars or {}

        self.inventory['_meta']['hostvars'].setdefault(host, {}).update(vars)

        if group:
            self.add_group(group=group, group_vars=group_vars)
            if host not in self.inventory[group]['hosts']:
                self.inventory[group]['hosts'].append(host)
        else:
            if host not in self.inventory['ungrouped']['hosts']:
                self.inventory['ungrouped']['hosts'].append(host)

    def add_host_to_group(
            self, *, host: str, group: Optional[str] = None, vars: Optional[Dict] = None,
            group_vars: Optional[Dict] = None
            ) -> None:
        """
        Add an existing host to a group, or create and add the host if it doesn't exist,
        with optional host and group variables.

        Args:
            host (str): The host IP or name.
            group (str, optional): The group to add the host to.
            vars (Dict, optional): A dictionary of variables to associate with the host.
            group_vars (Dict, optional): A dictionary of variables to associate with the group.
        """
        vars = vars or {}
        group_vars = group_vars or {}

        self.inventory['_meta']['hostvars'].setdefault(host, {}).update(vars)

        if group:
            self.add_group(group=group, group_vars=group_vars)

            # Check and remove the host from 'ungrouped' if it exists there
            if host in self.inventory['ungrouped']['hosts']:
                self.inventory['ungrouped']['hosts'].remove(host)

            if host not in self.inventory[group]['hosts']:
                self.inventory[group]['hosts'].append(host)
        else:
            if host not in self.inventory['ungrouped']['hosts']:
                self.inventory['ungrouped']['hosts'].append(host)

    def add_child_group(self, *, parent_group: str, child_group: str, group_vars: Optional[Dict] = None) -> None:
        """
        Add a child group to an existing group with optional variables.

        Args:
            parent_group (str): The parent group to add the child group to.
            child_group (str): The child group to add.
            group_vars (Dict, optional): A dictionary of variables to associate with the child group.
        """
        self.add_group(group=parent_group)
        self.add_group(group=child_group, group_vars=group_vars)

        if 'children' not in self.inventory[parent_group]:
            self.inventory[parent_group]['children'] = []
        if child_group not in self.inventory[parent_group]['children']:
            self.inventory[parent_group]['children'].append(child_group)

    def add_group_vars(self, *, group: str, group_vars: Dict) -> None:
        """
        Add variables to a group.

        Args:
            group (str): The group to add the variables to.
            group_vars (Dict): A dictionary of variables to associate with the group.
        """
        self.add_group(group=group)
        if 'vars' not in self.inventory[group]:
            self.inventory[group]['vars'] = {}
        self.inventory[group]['vars'].update(group_vars)

    def get_hosts(self) -> Dict[str, Dict]:
        """
        Retrieve the hosts from '_meta -> hostvars'.

        Returns:
            Dict[str, Dict]: A dictionary of hosts and their variables.
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

    def get_hosts_in_group(self, group: str) -> List[str]:
        """
        Retrieve all hosts that belong to a specified group.

        Args:
            group (str): The group to retrieve hosts from.

        Returns:
            List[str]: A list of host names.
        """
        if group in self.inventory:
            return self.inventory[group].get('hosts', [])
        return []

    def get_host(self, host: str) -> Optional[Dict]:
        """
        Retrieve the variables associated with a specific host.

        Args:
            host (str): The host to retrieve variables for.

        Returns:
            Optional[Dict]: A dictionary of variables associated with the host, or None if the host doesn't exist.
        """
        return self.inventory['_meta']['hostvars'].get(host)

    def get_group(self, group: str) -> Optional[Dict]:
        """
        Retrieve the variables associated with a specific group.

        Args:
            group (str): The group to retrieve variables for.

        Returns:
            Optional[Dict]: A dictionary of variables associated with the group, or None if the group doesn't exist.
        """
        if group in self.inventory:
            return self.inventory[group].get('vars', {})
        return None


def main():
    parser = argparse.ArgumentParser(description='Command line arguments for Ansible Dynamic Inventory.')
    parser.add_argument('--list', action='store_true', help='Return list of hosts.')
    parser.add_argument('--host', type=str, help='Return the requested host.')
    args = parser.parse_args()

    inventory = AnsibleDynamicInventory()

    # Example of adding multiple hosts to a group with variables
    inventory.add_hosts(
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
    inventory.add_hosts(
        hosts=['host2'], group='group2',
        vars={
            'ansible_host': '192.168.1.11',
            'ansible_user': 'user2',
            'ansible_ssh_private_key_file': '/path/to/private/key'
        }
    )

    # Example of adding a single host to the 'ungrouped' group
    inventory.add_host(
        host='host3', group=None, vars={
            'ansible_host': '192.168.1.12',
            'ansible_user': 'user3',
            'ansible_ssh_private_key_file': '/path/to/private/key'
        }
    )

    # Example of adding an existing host to another group
    inventory.add_host_to_group(host='host1', group='group2')

    # Example of adding a child group to a group with variables
    inventory.add_child_group(
        parent_group='group1', child_group='child_group1',
        group_vars={
            'var1': 'value1',
            'var2': 'value2'
        }
    )

    if args.list:
        print(json.dumps(inventory.inventory, indent=4))
    elif args.host:
        print(json.dumps(inventory.get_host(args.host), indent=4))

    # Loop through hosts
    print("Hosts:")
    for host in inventory.get_hosts():
        print(host)

    # Loop through groups
    print("\nGroups:")
    for group in inventory.get_groups():
        print(group)

    # Loop through child groups of 'group1'
    print("\nChild groups of 'group1':")
    for child_group in inventory.get_child_groups('group1'):
        print(child_group)

    # Get all hosts in a specified group
    print("\nAll hosts of group 'group1':")
    group_name = 'group1'
    hosts_in_group = inventory.get_hosts_in_group(group_name)
    print(f"Hosts in group '{group_name}':", hosts_in_group)

    print("\nVariables for 'host1':")
    host_vars = inventory.get_host('host1')
    print(host_vars)

    print("\nVariables for 'group1':")
    group_vars = inventory.get_group('group1')
    print(group_vars)


if __name__ == '__main__':
    main()
