# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enamel.tests.unit import base

from enamel.api import version


class TestVersion(base.TestCase):

    def test_version_parses(self):
        request_version = version.Version.parse_version_string('10.5')
        self.assertEqual(10, request_version.major)
        self.assertEqual(5, request_version.minor)

    def test_version_negative(self):
        request_version = version.Version.parse_version_string('-10.5')
        self.assertEqual(-10, request_version.major)
        self.assertEqual(5, request_version.minor)

    def test_version_fails_no_split(self):
        self.assertRaises(ValueError,
                          version.Version.parse_version_string,
                          '105')

    def test_version_fails_not_numbers(self):
        self.assertRaises(ValueError,
                          version.Version.parse_version_string,
                          'Nancy, could you bring me the newspaper?')

    def test_version_fails_not_numbers_w_dot(self):
        self.assertRaises(ValueError,
                          version.Version.parse_version_string,
                          'Nancy, could you.bring me the newspaper?')

    def test_version_fails_empty(self):
        self.assertRaises(ValueError,
                          version.Version.parse_version_string,
                          '')

    def test_version_latest(self):
        request_version = version.Version.parse_version_string('latest')
        max_version = version.Version.parse_version_string(
            version.max_version_string())
        self.assertEqual(max_version, request_version)

    def test_versions_compare(self):
        min_version = version.Version.parse_version_string(
            version.min_version_string())
        max_version = version.Version.parse_version_string(
            version.min_version_string())

        self.assertLessEqual(min_version, max_version)

        huge_version = version.Version.parse_version_string('99999.99999')
        self.assertGreater(huge_version, min_version)

    def test_header_is_good(self):
        self.assertEqual('OpenStack-enamel-API-Version',
                         version.Version.header)

        request_version = version.Version.parse_version_string('latest')
        self.assertEqual('OpenStack-enamel-API-Version',
                         request_version.header)


class TestHeaderExtraction(base.TestCase):

    def test_correct_headers(self):
        headers = {'openstack-enamel-api-version':
                   '0.9'}
        request_version = version.extract_version(headers)
        self.assertEqual(version.Version.parse_version_string('0.9'),
                         request_version)

    def test_valid_number_but_not_listed_version(self):
        headers = {'openstack-enamel-api-version':
                   '0.8'}
        self.assertRaises(ValueError, version.extract_version, headers)

    def test_missing_header(self):
        headers = {}
        request_version = version.extract_version(headers)
        min_version = version.MIN_VERSION
        self.assertEqual(min_version, request_version)

    def test_latest_header(self):
        headers = {'openstack-enamel-api-version':
                   'latest'}
        request_version = version.extract_version(headers)
        max_version = version.MAX_VERSION
        self.assertEqual(max_version, request_version)

    def test_huge_header(self):
        headers = {'openstack-enamel-api-version':
                   '9999.9999'}
        self.assertRaises(ValueError, version.extract_version, headers)

    def test_weird_header(self):
        headers = {'openstack-enamel-api-version':
                   '1.0 bottles of sangria'}
        self.assertRaises(ValueError, version.extract_version, headers)

    def test_whitespacey_header(self):
        headers = {'openstack-enamel-api-version':
                   '  1.0         '}
        request_version = version.extract_version(headers)
        self.assertEqual(version.Version(1, 0), request_version)

    def test_weird_whitespacey_header(self):
        headers = {'openstack-enamel-api-version':
                   '  1  .   0         '}
        request_version = version.extract_version(headers)
        self.assertEqual(version.Version(1, 0), request_version)

    def test_cows_in_header(self):
        headers = {'openstack-enamel-api-version':
                   '  1  .   cow         '}
        self.assertRaises(ValueError, version.extract_version, headers)

    def test_negative_header(self):
        headers = {'openstack-enamel-api-version':
                   ' -1.9'}
        self.assertRaises(ValueError, version.extract_version, headers)
