#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

"""A Charm to functionally test the Grafana Operator."""

import logging

from charms.grafana_auth.v0.grafana_auth import AuthRequirer
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvider
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

logger = logging.getLogger(__name__)


class GrafanaTesterCharm(CharmBase):
    """A Charm used to test the Grafana charm."""

    def __init__(self, *args):
        super().__init__(*args)
        self._name = "grafana-tester"
        self.grafana_source = GrafanaSourceProvider(self, source_type="prometheus")
        self.grafana_dashboard = GrafanaDashboardProvider(self)
        self.grafana_auth_proxy_provider = AuthRequirer(self, urls=["https://wwww.example.com"])
        self.framework.observe(
            self.on.grafana_tester_pebble_ready, self._on_grafana_tester_pebble_ready
        )

        self.framework.observe(self.on.config_changed, self._on_config_changed)

        self.framework.observe(
            self.grafana_auth_proxy_provider.on.auth_conf_available,
            self._on_auth_config_available,
        )

    def _on_grafana_tester_pebble_ready(self, _):
        """Just set it ready. It's a pause image."""
        self.unit.status = ActiveStatus()

    def _on_config_changed(self, _):
        """Reconfigure the Grafana tester."""
        container = self.unit.get_container(self._name)
        if not container.can_connect():
            self.unit.status = BlockedStatus("Waiting for Pebble ready")
            return

        self.unit.status = ActiveStatus()

    def _on_auth_config_available(self, event):
        if not event.auth:
            self.unit.status = BlockedStatus("Waiting for authentication configuration")
            return
        self.auth = event.auth
        logger.info("auth config has been set: {}".format(self.auth))
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(GrafanaTesterCharm)
