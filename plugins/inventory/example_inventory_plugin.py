"""
The inventory plugin fetches data from a remote source into an Ansible inventory.
Note: The data generated is all fake using the Python Faker module.
"""

# Python built-in imports
import re
from typing import Any, Dict

# Ansible imports
from ansible.utils.display import Display
from ansible.module_utils.basic import to_native
from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.inventory.group import to_safe_group_name

from ansible_collections.homelab.example_collection.plugins.plugins_utils.fetch_data_func import fetch_data

DOCUMENTATION = r"""
name: example_inventory_plugin
plugin_type: inventory
short_description: Returns Ansible inventory from fake generated data
description: Returns Ansible inventory from fake generated data
options:
    devices:
        description: The number of devices to generate for the inventory
        required: false
        type: int
    filter_group_name:
        description: Filter inventory to only include hosts from the specified group
        required: false
        type: list[str]
    filter_exclude_host:
        description: Filter inventory hosts to exclude any host that matches the regex pattern
        required: false
        type: list[dict]
"""

EXAMPLE = r"""
plugin: homelab.example_collection.example_inventory_plugin
strict: false
devices: 5
keyed_groups:
  - key: site | lower
    prefix: site
    separator: '_'
compose:
  custom_var: "'test custom var'"
groups:
  desktops: "inventory_hostname.startswith('desktop')"
  devices_to_update: "'15.6.7' in ios_version"
filter_group_name:
  - devices_to_update
filter_exclude_host:
  - key: ios_version
    regex: ^15[.].*
"""

display = Display()


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    """
    Ansible inventory plugin that fetches data from a remote source.

    Attributes:
        NAME (str): The name of the inventory plugin.
    """

    NAME = "homelab.example_collection.example_inventory_plugin"

    def verify_file(self, path: str) -> bool:
        """
        Return true/false if this is possibly a valid file for this plugin to consume.

        Args:
            path (str): The path to the inventory file.

        Returns:
            bool: True if the file is valid, False otherwise.
        """
        valid = super().verify_file(path)
        return valid and path.endswith(("inventory.yml", "inventory.yaml", "inv.yml", "inv.yaml"))

    def parse(
        self, inventory: Any, loader: Any, path: str, cache: bool = False
    ) -> None:
        """
        Parse the inventory file and populate the Ansible inventory.

        Args:
            inventory (Any): The Ansible inventory object.
            loader (Any): The Ansible data loader.
            path (str): The path to the inventory file.
            cache (bool, optional): Whether to use cached data. Defaults to False.

        Raises:
            AnsibleParserError: If the path is not set correctly.
        """
        super().parse(inventory, loader, path, cache)

        if not path:
            raise AnsibleParserError("Path is not set correctly.")

        config_data: Dict[str, Any] = self._read_config_data(path)
        fetched_data = fetch_data(config_data)

        for device in fetched_data:
            try:
                group = to_safe_group_name(device["site"], replacer="_", force=True)
                name = device.pop("node_name")
                inventory.add_group(group=group)
                inventory.add_host(host=name, group=group)
                for key, value in device.items():
                    inventory.set_variable(name, key, value)
            except KeyError as error:
                display.warning(f"Missing expected key: {to_native(error)}")

            self._set_composite_vars(config_data.get("compose"), device, name, strict=config_data.get("strict", False))
            self._add_host_to_composed_groups(config_data.get("groups"), device, name, strict=config_data.get("strict", False))
            self._add_host_to_keyed_groups(
                config_data.get("keyed_groups"), device, name, strict=config_data.get("strict", False)
                )

        if filter_group_names := config_data.get("filter_group_name"):
            for group_name in list(inventory.get_groups_dict().keys()):
                if group_name.lower() not in [grp.lower() for grp in filter_group_names]:
                    inventory.remove_group(group_name)

        if filter_exclude_hosts := config_data.get("filter_exclude_host"):
            hosts_to_remove = [
                host for host in inventory.hosts.values()
                for exclude in filter_exclude_hosts
                if re.match(exclude["regex"], host.vars.get(exclude["key"], ""), flags=re.IGNORECASE)
            ]
            for host in hosts_to_remove:
                inventory.remove_host(host)

        inventory.reconcile_inventory()
