#!/bin/bash -xe

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# NOTE(cdent): Once we are integrated with the gate this will be
# executed as a post_test_hook in devstack gate. However for now it
# is something that can be executed manually.

# If we're running in the gate find our keystone endpoint to give to
# gabbi tests and do a chown. This allows us to set up the necessary
# environment.
if [ -d $BASE/new/devstack ]; then
    export ENAMEL_DIR="$BASE/new/enamel"
    STACK_USER=stack
    sudo chown -R $STACK_USER:stack $ENAMEL_DIR
    source $BASE/new/devstack/openrc admin admin
    # Go to the enamel dir
    cd $ENAMEL_DIR
fi

export ENAMEL_SERVICE_URL=$(openstack catalog show enamel -c endpoints -f value | awk '/public/{print $2}')
# Whether this is admin or demo depends on how openrc was sourced.
export AUTH_TOKEN=$(openstack token issue -c id -f value)

# Run the gabbi live integration tests
sudo -E -H -u ${STACK_USER:-${USER}} tox -eintegration

# TODO(cdent): Add test reporting.
