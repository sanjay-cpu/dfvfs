#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Script to check for the availability and version of dependencies."""

import re
import urllib2


def GetLibyalGoogleDriveVersion(library_name):
  """Retrieves the version number for a given libyal library on Google Drive.

  Args:
    library_name: the name of the libyal library.

  Returns:
    The latest version for a given libyal library on Google Drive
    or 0 on error.
  """
  url = 'https://code.google.com/p/{0}/'.format(library_name)

  url_object = urllib2.urlopen(url)

  if url_object.code != 200:
    return None

  data = url_object.read()

  # The format of the library downloads URL is:
  # https://googledrive.com/host/{random string}/
  expression_string = (
      '<a href="(https://googledrive.com/host/[^/]*/)"[^>]*>Downloads</a>')
  matches = re.findall(expression_string, data)

  if not matches or len(matches) != 1:
    return 0

  url_object = urllib2.urlopen(matches[0])

  if url_object.code != 200:
    return 0

  data = url_object.read()

  # The format of the library download URL is:
  # /host/{random string}/{library name}-{status-}{version}.tar.gz
  # Note that the status is optional and will be: beta, alpha or experimental.
  expression_string = '/host/[^/]*/{0}-[a-z-]*([0-9]+)[.]tar[.]gz'.format(
      library_name)
  matches = re.findall(expression_string, data)

  if not matches:
    return 0

  return int(max(matches))


def CheckLibyal(libyal_python_modules):
  """Checks the availability of libyal libraries.

  Args:
    libyal_python_modules: list of libyal python module names.

  Returns:
    True if the libyal libraries are available, false otherwise.
  """
  result = True
  for module_name in libyal_python_modules:
    try:
      module_object = map(__import__, [module_name])[0]
    except ImportError:
      print u'[FAILURE]\tmissing: {0:s}.'.format(module_name)
      result = False

    if result:
      libyal_name = u'lib{}'.format(module_name[2:])

      installed_version = int(module_object.get_version())
      try:
        latest_version = GetLibyalGoogleDriveVersion(libyal_name)
      except urllib2.URLError:
        print (
            u'Unable to verify version of {0:s} ({1:s}).\n'
            u'Does this system have Internet access?').format(
                libyal_name, module_name)
        result = False
        break

      version_mismatch = installed_version != latest_version
      if version_mismatch:
        print (
            u'[WARNING]\t{0:s} ({1:s}) version mismatch: installed {2:d}, '
            u'available: {3:d}').format(
                libyal_name, module_name, installed_version, latest_version)
      else:
        print u'[OK]\t\t{0:s} ({1:s}) version: {2:d}'.format(
            libyal_name, module_name, installed_version)

  return result


def CheckPythonModule(module_name, version_attribute_name, minimum_version):
  """Checks the availability of a Python module.

  Args:
    module_name: the name of the module.
    version_attribute_name: the name of the attribute that contains the module
                            version.
    minimum_version: the minimum required version.

  Returns:
    True if the Python module is available and conforms to the minimum required
    version. False otherwise.
  """
  result = True
  try:
    module_object = map(__import__, [module_name])[0]
  except ImportError:
    print u'[FAILURE]\tmissing: {0:s}.'.format(module_name)
    result = False

  if result:
    module_version = getattr(module_object, version_attribute_name, None)

    # Split the version string and convert every digit into an integer.
    # A string compare of both version strings will yield an incorrect result.
    module_version_map = map(int, module_version.split('.'))
    minimum_version_map = map(int, minimum_version.split('.'))
    if module_version_map < minimum_version_map:
      result = False
      print (
          u'[FAILURE]\t{0:s} version: {1:s} is too old, {2:s} or later '
          u'required.').format(module_name, module_version, minimum_version)
    else:
      print u'[OK]\t\t{0:s} version: {1:s}'.format(
          module_name, module_version)

  return result


def CheckPytsk():
  """Checks the availability of pytsk3.

  Returns:
    True if the pytsk3 Python module is available, false otherwise.
  """
  result = True
  module_name = 'pytsk3'
  minimum_version = '4.1.2'
  try:
    module_object = map(__import__, [module_name])[0]
  except ImportError:
    print u'[FAILURE]\tmissing: {0:s}.'.format(module_name)
    result = False

  if result:
    module_version = module_object.TSK_VERSION_STR

    # Split the version string and convert every digit into an integer.
    # A string compare of both version strings will yield an incorrect result.
    module_version_map = map(int, module_version.split('.'))
    minimum_version_map = map(int, minimum_version.split('.'))
    if module_version_map < minimum_version_map:
      result = False
      print (
          u'[FAILURE]\tSleuthKit version: {0:s} is too old, {1:s} or later '
          u'required.').format(module_version, minimum_version)
    else:
      print u'[OK]\t\t{0:s} version: {1:s}'.format(
          module_name, module_version)

    # TODO: check version of pytsk3 itself.

  return result


if __name__ == '__main__':
  check_result = True
  print u'Checking availability and versions of PyVFS dependencies.'

  if not CheckPythonModule('construct', '__version__', '2.5.1'):
    check_result = False

  # TODO: determine the version of protobuf.

  if not CheckPytsk():
    check_result = False

  if not CheckLibyal(['pyewf', 'pyqcow', 'pyvhdi', 'pyvshadow']):
    check_result = False

  if not check_result:
    installation_instructions_url = (
        u'https://code.google.com/p/pyvfs/wiki/Installing')

    print u'For more information on how to set up PyVFS see: {0:s}'.format(
        installation_instructions_url)

  print u''
