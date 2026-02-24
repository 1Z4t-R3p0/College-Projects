#!/bin/bash
set -e

# Wait for the image's internal initialization to have a chance (s6-overlay usually takes over)
# However, for Wazuh Manager, the ossec.conf needs to be right BEFORE the services start.

# In the wazuh-manager image, /var/ossec/etc/ is often populated by /init.
# If we replace ossec.conf, we do it here.

if [ -f /var/ossec/etc/ossec.conf.custom ]; then
    echo "Found custom ossec.conf. Waiting for base etc directory..."
    # Small sleep to ensure the internal /init has formatted the volume if any
    sleep 5
    echo "Applying custom ossec.conf..."
    cp /var/ossec/etc/ossec.conf.custom /var/ossec/etc/ossec.conf
    chown root:wazuh /var/ossec/etc/ossec.conf
    chmod 660 /var/ossec/etc/ossec.conf
fi

# Execute the original init
echo "Starting Wazuh Manager via /init..."
exec /init
