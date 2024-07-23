#!/usr/bin/env python3

import argparse
import json
import yaml
import os
from typing import List, Dict, Optional


CACHE_DIR = '.cache'
CACHE_FILE = os.path.join(CACHE_DIR, 'inventory_cache.json')


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

    def remove_group(self, group: str) -> None:
        """
        Remove a group from the inventory, including from any parent groups' children lists.

        Args:
            group (str): The group to remove.
        """
        if group in self.inventory:
            del self.inventory[group]
        if group in self.inventory['all']['children']:
            self.inventory['all']['children'].remove(group)

        for g, g_data in self.inventory.items():
            if 'children' in g_data and group in g_data['children']:
                g_data['children'].remove(group)

    def remove_host(self, host: str) -> None:
        """
        Remove a host from the inventory and any group the host belongs to.

        Args:
            host (str): The host to remove.
        """
        if host in self.inventory['_meta']['hostvars']:
            del self.inventory['_meta']['hostvars'][host]

        for g, g_data in self.inventory.items():
            if g == '_meta':
                continue
            if 'hosts' in g_data and host in g_data['hosts']:
                g_data['hosts'].remove(host)

    @staticmethod
    def load_cache() -> 'AnsibleDynamicInventory':
        """Loads the inventory from the cache file."""
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as file:
                try:
                    inventory_data = json.load(file)
                except json.JSONDecodeError:
                    return AnsibleDynamicInventory()
                inventory = AnsibleDynamicInventory()
                inventory.inventory = inventory_data
                return inventory
        return AnsibleDynamicInventory()

    @staticmethod
    def save_cache(inventory: 'AnsibleDynamicInventory') -> None:
        """Saves the inventory to the cache file."""
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(CACHE_FILE, 'w') as file:
            json.dump(inventory.inventory, file)

    @staticmethod
    def delete_cache() -> None:
        """Deletes the cache file if it exists."""
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)


def generate_inventory(inventory: AnsibleDynamicInventory) -> None:
    # Example of adding multiple hosts to a group with variables
    print('CALLED GENERATE INVENTORY')
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


def main():
    parser = argparse.ArgumentParser(description='Ansible Dynamic Inventory Script')
    parser.add_argument('--list', action='store_true', help='List all hosts (default Ansible option)')
    parser.add_argument('--host', help='Get variables for a specific host (default Ansible option)')
    parser.add_argument('--group', help='List all hosts in a specific group')
    parser.add_argument('--output', choices=['json', 'yaml'], help='Output format: json or yaml')
    parser.add_argument('--export', help='Export inventory to a file (extension added automatically)')
    parser.add_argument('--cache', choices=['on', 'off'], help='Enable or disable cache')

    args = parser.parse_args()

    if not (args.list or args.host or args.group):
        parser.error('At least one of --list, --host, or --group must be specified.')

    cache_option = args.cache.lower() if args.cache else None

    if cache_option == 'off':
        AnsibleDynamicInventory.delete_cache()
        inventory = AnsibleDynamicInventory()
        generate_inventory(inventory)
    elif cache_option == 'on':
        inventory = AnsibleDynamicInventory.load_cache()
        if not inventory.get_hosts():
            generate_inventory(inventory)
            AnsibleDynamicInventory.save_cache(inventory)
    else:
        inventory = AnsibleDynamicInventory()
        generate_inventory(inventory)

    if args.list:
        output = inventory.inventory
    elif args.host:
        output = inventory.get_host(args.host)
    elif args.group:
        output = inventory.get_group(args.group)

    if args.output == 'json':
        output_str = json.dumps(output, indent=4)
    elif args.output == 'yaml':
        output_str = yaml.dump(output, default_flow_style=False)
    else:
        output_str = json.dumps(output)  # Default to JSON without indent

    if args.export:
        file_base, _ = os.path.splitext(args.export)
        if args.output == 'yaml':
            file_extension = '.yaml'
        else:
            file_extension = '.json'
        file_path = f"{file_base}{file_extension}"
        with open(file_path, 'w') as file:
            file.write(output_str)
        print(f"Inventory has been exported to {file_path}")
    else:
        print(output_str)


if __name__ == '__main__':
    main()
