#!/usr/bin/env python3

import argparse
import json
from typing import List, Dict, Optional


class ExampleInventory:
    def __init__(self):
        self.inventory = {
            '_meta': {
                'hostvars': {}
            },
            'all': {
                'children': [
                    'ungrouped'
                ]
            }
        }

    def add_hosts(self, group: str,
                  hosts: Optional[List[str]] = None, vars: Optional[Dict] = None) -> None:
        """
        Add multiple hosts to a group with optional variables.
        
        Args:
            group (str): The group to add the hosts to.
            hosts (List[str], optional): A list of host IPs or names.
            vars (Dict, optional): A dictionary of variables to associate with the hosts.
        """
        hosts = hosts or []
        vars = vars or {}

        self._ensure_group_exists(group)
        self.inventory.setdefault(group, {}).setdefault('hosts', []).extend(hosts)

        for host in hosts:
            self.inventory['_meta']['hostvars'][host] = vars

    def add_host(self, group: str,
                 host: str, vars: Optional[Dict] = None) -> None:
        """
        Add a single host to a group with optional variables.
        
        Args:
            group (str): The group to add the host to.
            host (str): The host IP or name.
            vars (Dict, optional): A dictionary of variables to associate with the host.
        """
        vars = vars or {}

        self._ensure_group_exists(group)
        self.inventory.setdefault(group, {}).setdefault('hosts', [])
        if host not in self.inventory[group]['hosts']:
            self.inventory[group]['hosts'].append(host)

        self.inventory['_meta']['hostvars'][host] = vars

    def add_child_group(self, parent_group: str, child_group: str) -> None:
        """
        Add a child group to an existing group.
        
        Args:
            parent_group (str): The parent group to add the child group to.
            child_group (str): The child group to add.
        """
        self._ensure_group_exists(parent_group)
        self._ensure_group_exists(child_group)
        
        self.inventory.setdefault(parent_group, {}).setdefault('children', [])
        if child_group not in self.inventory[parent_group]['children']:
            self.inventory[parent_group]['children'].append(child_group)

    def _ensure_group_exists(self, group: str) -> None:
        """
        Ensure that a group exists in the 'all' children list.
        
        Args:
            group (str): The group to ensure existence of.
        """
        if group not in self.inventory['all']['children']:
            self.inventory['all']['children'].append(group)
        self.inventory.setdefault(group, {}).setdefault('hosts', [])


def main():
    parser = argparse.ArgumentParser(
        description='Command line arguments for Ansible Dynamic Inventory.')
    parser.add_argument(
        '--list', action='store_true', help='Return list of hosts.')
    parser.add_argument('--host', type=str, help='Return the requested host.')
    args = parser.parse_args()

    example_inventory = ExampleInventory()

    # Sample data for demonstration
    example_inventory.add_hosts(
        group='dbservers', hosts=['10.0.0.5', '10.0.0.1'],
        vars={'http_port': 80}
    )
    example_inventory.add_host(
        group='test_group', host='10.0.0.20', vars={'type': 'switch'}
    )
    example_inventory.add_child_group(
        parent_group='test_group', child_group='dbservers'
    )

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
