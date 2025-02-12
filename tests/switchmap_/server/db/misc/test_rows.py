#!/usr/bin/env python3
"""Test the Rows module."""
import os
import sys
import unittest

# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.abspath(
            os.path.join(
                os.path.abspath(
                    os.path.join(
                        os.path.abspath(
                            os.path.join(
                                os.path.abspath(
                                    os.path.join(EXEC_DIR, os.pardir)
                                ),
                                os.pardir,
                            )
                        ),
                        os.pardir,
                    )
                ),
                os.pardir,
            )
        ),
        os.pardir,
    )
)
_EXPECTED = """\
{0}switchmap-ng{0}tests{0}switchmap_{0}server{0}db{0}misc""".format(
    os.sep
)
if EXEC_DIR.endswith(_EXPECTED) is True:
    sys.path.insert(0, ROOT_DIR)
else:
    print(
        """This script is not installed in the "{0}" directory. Please fix.\
""".format(
            _EXPECTED
        )
    )
    sys.exit(2)

from tests.testlib_ import setup

CONFIG = setup.config()
CONFIG.save()

from switchmap.server.db import models
from switchmap.server.db.misc import rows
from switchmap.server.db.table import zone
from switchmap.server.db.table import event
from switchmap.server.db.table import device
from switchmap.server.db.table import l1interface
from switchmap.server.db.table import IDevice
from switchmap.server.db.table import IL1Interface
from switchmap.server.db.table import IZone
from switchmap.server.db.table import IRoot
from switchmap.server.db.table import root as root_table
from tests.testlib_ import db
from tests.testlib_ import data


class TestRows(unittest.TestCase):
    """Checks all functions and methods."""

    @classmethod
    def setUpClass(cls):
        """Setup database for testing."""
        # Initialize config
        config = setup.config()
        config.save()

        # Drop and recreate database
        database = db.Database()
        database.drop()
        models.create_all_tables()

    def setUp(self):
        """Setup the database prior to each test."""
        # Create base event for tests
        self.event_row = event.create()

        # Create base zone for tests
        self.zone_name = data.random_string()
        zone_data = IZone(
            idx_event=self.event_row.idx_event,
            name=self.zone_name,
            notes=data.random_string(),
            enabled=1,
        )
        zone.insert_row(zone_data)
        self.zone_record = zone.exists(
            self.event_row.idx_event, self.zone_name
        )

    def test_device_success(self):
        """Testing function device with valid device data."""
        # Create test device
        test_device = IDevice(
            idx_zone=self.zone_record.idx_zone,
            hostname="test_host",
            name="test_name",
            sys_name="test_sys_name",
            sys_description=data.random_string(),
            sys_objectid=data.random_string(),
            sys_uptime=1000,
            last_polled=2000,
            enabled=1,
        )
        device.insert_row(test_device)

        device_record = device.exists(self.zone_record.idx_zone, "test_host")

        # Test rows.device function
        result = rows.device(device_record)

        # Verify results
        self.assertEqual(result.idx_device, device_record.idx_device)
        self.assertEqual(result.hostname.decode(), "test_host")
        self.assertEqual(result.name.decode(), "test_name")
        self.assertEqual(result.sys_name.decode(), "test_sys_name")

    def test_device_not_exists(self):
        """Testing function device with non-existent device."""
        result = rows.device(None)
        self.assertIsNone(result)

    def test_l1interface_success(self):
        """Testing function l1interface with valid interface data."""
        # Create device first
        test_device = IDevice(
            idx_zone=self.zone_record.idx_zone,
            hostname="test_host",
            name="test_name",
            sys_name="test_sys_name",
            sys_description=data.random_string(),
            sys_objectid=data.random_string(),
            sys_uptime=1000,
            last_polled=2000,
            enabled=1,
        )
        device.insert_row(test_device)
        device_record = device.exists(self.zone_record.idx_zone, "test_host")

        # Create test interface
        test_interface = IL1Interface(
            idx_device=device_record.idx_device,
            ifindex=1,
            duplex=1,
            ethernet=1,
            nativevlan=1,
            trunk=0,
            iftype=6,
            ifspeed=1000000000,
            ifalias="Test Interface",
            ifname="Gi0/1",
            ifdescr="GigabitEthernet0/1",
            ifadminstatus=1,
            ifoperstatus=1,
            ts_idle=0,
            cdpcachedeviceid="",
            cdpcachedeviceport="",
            cdpcacheplatform="",
            lldpremportdesc="",
            lldpremsyscapenabled="",
            lldpremsysdesc="",
            lldpremsysname="",
            enabled=1,
        )
        l1interface.insert_row(test_interface)

        interface_record = l1interface.exists(
            device_record.idx_device, test_interface.ifindex
        )

        # Test rows.l1interface function
        result = rows.l1interface(interface_record)

        # Verify results
        self.assertEqual(result.ifindex, 1)
        self.assertEqual(result.ifname.decode(), "Gi0/1")
        self.assertEqual(result.ifdescr.decode(), "GigabitEthernet0/1")
        self.assertEqual(result.ifalias.decode(), "Test Interface")

    def test_l1interface_not_exists(self):
        """Testing function l1interface with non-existent interface."""
        result = rows.l1interface(None)
        self.assertIsNone(result)

    def test_root_success(self):
        """Testing function root with valid root data."""
        # Create test root
        root_name = data.random_string()
        test_root = IRoot(
            idx_event=self.event_row.idx_event, name=root_name, enabled=1
        )
        root_table.insert_row(test_root)

        root_record = root_table.exists(root_name)

        # Test rows.root function
        result = rows.root(root_record)

        # Verify results
        self.assertEqual(result.idx_root, root_record.idx_root)
        self.assertEqual(result.name.decode(), root_name)

    def test_root_not_exists(self):
        """Testing function root with non-existent root."""
        result = rows.root(None)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
