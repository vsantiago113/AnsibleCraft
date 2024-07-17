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
                'hosts': []
            }
        }

    def add_hosts(self, *, hosts: Optional[List[str]] = None, group: str, vars: Optional[Dict] = None) -> None:
        """
        Add multiple hosts to a group with optional variables.

        Args:
            group (str): The group to add the hosts to.
            hosts (List[str], optional): A list of host IPs or names.
            vars (Dict, optional): A dictionary of variables to associate with the hosts.
        """
        hosts = hosts or []
        vars = vars or {}

        for host in hosts:
            self.add_host(host=host, group=group, vars=vars)

    def add_host(self, *, host: str, group: Optional[str], vars: Optional[Dict] = None) -> None:
        """
        Add a single host to a group with optional variables.

        Args:
            group (str): The group to add the host to.
            host (str): The host IP or name.
            vars (Dict, optional): A dictionary of variables to associate with the host.
        """
        vars = vars or {}

        self.inventory['_meta']['hostvars'].setdefault(host, {}).update(vars)

        if group:
            self._ensure_group_exists(group=group)
            if host not in self.inventory[group]['hosts']:
                self.inventory[group]['hosts'].append(host)
        else:
            if host not in self.inventory['ungrouped']['hosts']:
                self.inventory['ungrouped']['hosts'].append(host)

    def add_host_to_group(self, *, host: str, group: str, vars: Optional[Dict] = None) -> None:
        """
        Add an existing host to a group, or create and add the host if it doesn't exist.

        Args:
            group (str): The group to add the host to.
            host (str): The host IP or name.
            vars (Dict, optional): A dictionary of variables to associate with the host.
        """
        self.add_host(host=host, group=group, vars=vars)

    def add_child_group(self, *, parent_group: str, child_group: str) -> None:
        """
        Add a child group to an existing group.

        Args:
            parent_group (str): The parent group to add the child group to.
            child_group (str): The child group to add.
        """
        self._ensure_group_exists(group=parent_group)
        self._ensure_group_exists(group=child_group)

        if 'children' not in self.inventory[parent_group]:
            self.inventory[parent_group]['children'] = []
        if child_group not in self.inventory[parent_group]['children']:
            self.inventory[parent_group]['children'].append(child_group)

    def _ensure_group_exists(self, *, group: str) -> None:
        """
        Ensure that a group exists in the 'all' children list.

        Args:
            group (str): The group to ensure existence of.
        """
        if group not in self.inventory['all']['children']:
            self.inventory['all']['children'].append(group)
        if group not in self.inventory:
            self.inventory[group] = {'hosts': []}


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

    # Example of adding a child group to a group
    example_inventory.add_child_group(parent_group='group1', child_group='child_group1')

    if args.list:
        print(json.dumps(example_inventory.inventory, indent=4))
    elif args.host:
        print(json.dumps(
            example_inventory.inventory['_meta']['hostvars'].get(
                args.host, {}
            ), indent=4
        ))


if __name__ == '__main__':
    main()
