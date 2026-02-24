FROM ubuntu:22.04

ARG WAZUH_VERSION=4.7.2

ENV DEBIAN_FRONTEND=noninteractive
ENV WAZUH_MANAGER=wazuh.manager
ENV WAZUH_AGENT_GROUP=default
ENV WAZUH_REGISTRATION_PASSWORD=SecretPassword

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    iproute2 \
    iptables \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Add Wazuh repository
RUN curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --dearmor -o /usr/share/keyrings/wazuh.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
    > /etc/apt/sources.list.d/wazuh.list && \
    apt-get update && \
    WAZUH_MANAGER=${WAZUH_MANAGER} apt-get install -y wazuh-agent=${WAZUH_VERSION}-1 && \
    rm -rf /var/lib/apt/lists/*

# Entrypoint: register + start agent
COPY agent-entrypoint.sh /agent-entrypoint.sh
RUN chmod +x /agent-entrypoint.sh

ENTRYPOINT ["/agent-entrypoint.sh"]
