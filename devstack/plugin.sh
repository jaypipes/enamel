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

# Enamel devstack plugin
# Install and starts the Enamel service.
#
# To enable enamel add the following to the localrc of local.conf:
# NOTE(cdent): Update this to openstack when the time comes.
#
#   enable_plugin gnocchi https://github.com/jaypipes/enamel
#
# This will turn on the enamel-api service.


# Save trace setting
XTRACE=$(set +o | grep xtrace)
set -o xtrace

function is_enamel_enabled {
    [[ ,${ENABLED_SERVICES} =~ ,"enamel-" ]] && return 0
    return 1
}

function _config_enamel_apache_wsgi {
    local enamel_apache_conf=$(apache_site_config_for enamel)
    local venv_path=""
    local script_name=$ENAMEL_SERVICE_PREFIX

    sudo install -d -o $STACK_USER $ENAMEL_WSGI_DIR

    if [[ ${USE_VENV} = True ]]; then
        venv_path="python-path=${PROJECT_VENV["enamel"]}/lib/$(python_version)/site-packages"
    fi

    # copy wsgi file
    sudo cp $ENAMEL_DIR/enamel/api/app.wsgi $ENAMEL_WSGI_DIR/

    sudo cp $ENAMEL_DIR/devstack/apache-enamel.template $enamel_apache_conf
    sudo sed -e "
            s|%SCRIPT_NAME%|$script_name|g;
            s|%APACHE_NAME%|$APACHE_NAME|g;
            s|%WSGI%|$ENAMEL_WSGI_DIR/app.wsgi|g;
            s|%USER%|$STACK_USER|g
            s|%APIWORKERS%|$API_WORKERS|g
            s|%VIRTUALENV%|$venv_path|g
        " -i $enamel_apache_conf
}

function enamel_service_url {
    if [ "$ENAMEL_USE_MOD_WSGI" == "True" ]; then
        echo "$ENAMEL_SERVICE_PROTOCOL://$ENAMEL_SERVICE_HOST$ENAMEL_SERVICE_PREFIX"
    else:
        echo "$ENAMEL_SERVICE_PROTOCOL://$ENAMEL_SERVICE_HOST:$ENAMEL_SERVICE_PORT"
    fi
}

function create_enamel_accounts {
    if is_service_enabled key && is_service_enabled enamel-api; then
        create_service_user "gnocchi"

        if [[ "$KEYSTONE_CATALOG_BACKEND" = 'sql' ]]; then
            local enamel_service=$(get_or_create_service $ENAMEL_SERVICE_NAME \
                                    $ENAMEL_SERVICE_TYPE "OpenStack ${ENAMEL_SERVICE_TYPE} Service")
            get_or_create_endpoint $enamel_service \
                "$REGION_NAME" \
                "$(enamel_service_url)" \
                "$(enamel_service_url)" \
                "$(enamel_service_url)"
        fi
    fi
}

function preinstall_enamel {
    echo "nothing to preinstall"
}

function install_enamel {
    # If Keystone is in use, install the middleware
    # NOTE(cdent): If we want to follow global requirements use
    # pip_install_gr here.
    is_service_enabled key && pip_install keystonemiddleware

    if [ "$ENAMEL_USE_MOD_WSGI" == "True" ]; then
        install_apache_wsgi
    fi

    # Create configuration directory
    [ ! -d $ENAMEL_CONF_DIR ] && sudo mkdir -m 755 -p $ENAMEL_CONF_DIR
    sudo chown $STACK_USER $ENAMEL_CONF_DIR

    # Install enamel itself.
    setup_develop $ENAMEL_DIR
}


function configure_enamel {
    # Configure logging
    iniset $ENAMEL_CONF DEFAULT debug "$ENABLE_DEBUG_LOG_LEVEL"

    if is_service_enabled key; then
        iniset $ENAMEL_CONF api auth_stategy "keystone"
        # NOTE(cdent): Set the rest when we know what we need?
        configure_auth_token_middleware $ENAMEL_CONF enamel $ENAMEL_AUTH_CACHE_DIR
    else
        iniset $ENAMEL_CONF api auth_strategy "None"
    fi

    if [ "$ENAMEL_USE_MOD_WSGI" == "True" ]; then
        _config_enamel_apache_wsgi
    else
        iniset $ENAMEL_CONF api bind_port $ENAMEL_SERVICE_PORT
        iniset $ENAMEL_CONF api bind_address $ENAMEL_SERVICE_HOST
    fi
}

function init_enamel {
    sudo install -d -o $STACK_USER -m 0700 $ENAMEL_AUTH_CACHE_DIR
    rm -f $ENAMEL_AUTH_CACHE_DIR/*

    # We want this to fail if there aren't any database servers,
    # so don't bother checking.
    recreate_database enamel

    # NOTE(cdent): When enamel-dbsync exists, remove the blocking
    # comment.
    # $ENAMEL_BIN_DIR/enamel-dbsync
}

function start_enamel {
    if is_service_enabled enamel-api; then
        if [[ "$ENAMEL_USE_MOD_WSGI" == "True" ]]; then
            enable_apache_site enamel
            restart_apache_server
            # NOTE(chdent): At the moment this is very noisy as it
            # will tail the entire apache logs, not just the gnocchi
            # parts. If you don't like this either USE_SCREEN=False
            # or moan at cdent to add support for PORT.
            tail_log enamel-error /var/log/$APACHE_NAME/error[_\.]log
            tail_log enamel-access /var/log/$APACHE_NAME/access[_\.]log
        else
            run_process enamel-api "$ENAMEL_BIN_DIR/enamel -d -v --config-file $ENAMEL_CONF"
        fi
    fi
}

function stop_enamel {
    if [ "$ENAMEL_USE_MOD_WSGI" == "True" ]; then
        disable_apache_site enamel
        restart_apache_server
    fi
    # Kill the enamel screen windows
    for serv in enamel-api; do
        stop_process $serv
    done
}

function cleanup_enamel {
    if [ "$ENAMEL_USE_MOD_WSGI" == "True" ]; then
        sudo rm -f $ENAMEL_WSGI_DIR/*.wsgi
        sudo rm -f $(apache_site_config_for enamel)
    fi
}

if is_service_enabled enamel-api; then
    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        echo_summary "Configuring system services for Enamel"
        preinstall_enamel
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Enamel"
        stack_install_service enamel
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Enamel"
        configure_enamel
        create_enamel_accounts
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing Enamel"
        init_enamel
        start_enamel
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Stopping Enamel"
        stop_enamel
    fi

    if [[ "$1" == "clean" ]]; then
        cleanup_enamel
    fi
fi
