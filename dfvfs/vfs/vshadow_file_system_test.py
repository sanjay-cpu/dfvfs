#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for a file system implementation using pyvshadow."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import vshadow_file_system


class VShadowFileSystemTest(unittest.TestCase):
  """The unit test for the VSS file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/', parent=self._qcow_path_spec)

  # qcowmount test_data/vsstest.qcow2 fuse/
  # vshadowinfo fuse/qcow1
  #
  # Volume Shadow Snapshot information:
  #   Number of stores:	2
  #
  # Store: 1
  #   ...
  #   Identifier		: 600f0b69-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID	: 0a4e3901-6abb-48fc-95c2-6ab9e38e9e71
  #   Creation time		: Dec 03, 2013 06:35:09.736378700 UTC
  #   Shadow copy ID		: 4e3c03c2-7bc6-4288-ad96-c1eac1a55f71
  #   Volume size		: 1073741824 bytes
  #   Attribute flags		: 0x00420009
  #
  # Store: 2
  #   Identifier		: 600f0b6d-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID	: 8438a0ee-0f06-443b-ac0c-2905647ca5d6
  #   Creation time		: Dec 03, 2013 06:37:48.919058300 UTC
  #   Shadow copy ID		: 18f1ac6e-959d-436f-bdcc-e797a729e290
  #   Volume size		: 1073741824 bytes
  #   Attribute flags		: 0x00420009

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = vshadow_file_system.VShadowFileSystem(self._resolver_context)
    self.assertNotEquals(file_system, None)

    file_system.Open(path_spec=self._vshadow_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = vshadow_file_system.VShadowFileSystem(self._resolver_context)
    self.assertNotEquals(file_system, None)

    file_system.Open(path_spec=self._vshadow_path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss2', parent=self._qcow_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=9, parent=self._qcow_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss0', parent=self._qcow_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss9', parent=self._qcow_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    file_system = vshadow_file_system.VShadowFileSystem(self._resolver_context)
    self.assertNotEquals(file_system, None)

    file_system.Open(path_spec=self._vshadow_path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'vss2')

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss2', parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'vss2')

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=9, parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEquals(file_entry, None)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss0', parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEquals(file_entry, None)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss9', parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEquals(file_entry, None)

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = vshadow_file_system.VShadowFileSystem(self._resolver_context)
    self.assertNotEquals(file_system, None)

    file_system.Open(path_spec=self._vshadow_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
