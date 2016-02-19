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

import fixtures

from enamel.tests.unit import base

from enamel.api import version


MOCK_VERSIONS = [
    '0.1',
    '0.9',
    '1.0',
]


class MockVersionedTest(base.TestCase):

    def setUp(self):
        self.useFixture(fixtures.MonkeyPatch(
            'enamel.api.version.VERSIONS', MOCK_VERSIONS))
        super(MockVersionedTest, self).setUp()


class TestVersion(MockVersionedTest):

    def test_version_parses(self):
        request_version = version.parse_version_string('10.5')
        self.assertEqual(10, request_version.major)
        self.assertEqual(5, request_version.minor)

    def test_version_negative(self):
        request_version = version.parse_version_string('-10.5')
        self.assertEqual(-10, request_version.major)
        self.assertEqual(5, request_version.minor)

    def test_version_fails_no_split(self):
        self.assertRaises(ValueError,
                          version.parse_version_string,
                          '105')

    def test_version_fails_not_numbers(self):
        self.assertRaises(ValueError,
                          version.parse_version_string,
                          'Nancy, could you bring me the newspaper?')

    def test_version_fails_not_numbers_w_dot(self):
        self.assertRaises(ValueError,
                          version.parse_version_string,
                          'Nancy, could you.bring me the newspaper?')

    def test_version_fails_empty(self):
        self.assertRaises(ValueError,
                          version.parse_version_string,
                          '')

    def test_version_latest(self):
        request_version = version.parse_version_string('latest')
        max_version = version.parse_version_string(
            version.max_version_string())
        self.assertEqual(max_version, request_version)

    def test_versions_compare(self):
        min_version = version.parse_version_string(
            version.min_version_string())
        max_version = version.parse_version_string(
            version.min_version_string())

        self.assertLessEqual(min_version, max_version)

        huge_version = version.parse_version_string('99999.99999')
        self.assertGreater(huge_version, min_version)

    def test_header_is_good(self):
        self.assertEqual('OpenStack-enamel-API-Version',
                         version.Version.HEADER)

        request_version = version.parse_version_string('latest')
        self.assertEqual('OpenStack-enamel-API-Version',
                         request_version.HEADER)

    def test_matches_does_match(self):
        request_version = version.parse_version_string('9.9')
        # Version is a tuple under the hood
        self.assertTrue(request_version.matches((1, 1), (10, 0)))

    def test_matches_does_not_match(self):
        request_version = version.parse_version_string('9.9')
        self.assertFalse(request_version.matches((10, 1), (75, 0)))

    def test_matches_does_not_match_weird(self):
        request_version = version.parse_version_string('9.9')
        self.assertFalse(request_version.matches((75, 1), (10, 0)))

    def test_matches_no_args_bad_version(self):
        request_version = version.parse_version_string('9.9')
        self.assertFalse(request_version.matches())

    def test_matches_no_args_good_version(self):
        request_version = version.parse_version_string('0.9')
        self.assertTrue(request_version.matches())

    def test_matches_max_arg(self):
        request_version = version.parse_version_string('0.9')
        self.assertTrue(request_version.matches(max_version=(0, 9)))

    def test_matches_min_arg(self):
        request_version = version.parse_version_string('0.9')
        self.assertTrue(request_version.matches(min_version=(0, 9)))

    def test_matches_min_arg_bad_version(self):
        request_version = version.parse_version_string('0.8')
        self.assertFalse(request_version.matches(min_version=(0, 9)))


class TestHeaderExtraction(MockVersionedTest):

    def test_correct_headers(self):
        headers = {'openstack-enamel-api-version':
                   '0.9'}
        request_version = version.extract_version(headers)
        self.assertEqual(version.parse_version_string('0.9'),
                         request_version)

    def test_valid_number_but_not_listed_version(self):
        headers = {'openstack-enamel-api-version':
                   '0.8'}
        self.assertRaises(ValueError, version.extract_version, headers)

    def test_missing_header(self):
        headers = {}
        request_version = version.extract_version(headers)
        self.assertEqual(request_version.min_version, request_version)

    def test_latest_header(self):
        headers = {'openstack-enamel-api-version':
                   'latest'}
        request_version = version.extract_version(headers)
        self.assertEqual(request_version.max_version, request_version)

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
