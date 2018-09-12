# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask_oidc import OpenIDConnect


class EstuaryOIDC(OpenIDConnect):
    """Customized version of flask_oidc.OpenIDConnect."""

    def load_secrets(self, app):
        """
        Get the configuration required to introspect tokens using flask_oidc.

        The default load_secrets method requires a large config file with many values that aren't
        used by Estuary. This method simplifies the configuration by using a few values from the
        Flask configuration.

        :param flask.Flask app: the flask app with the OpenID Connect configuration
        :return: a configuration in the format that flask_oidc expects
        :rtype: dict
        """
        return {
            'web': {
                'redirect_uris': None,
                'token_uri': None,
                'auth_uri': None,
                'client_id': app.config['OIDC_CLIENT_ID'],
                'client_secret': app.config['OIDC_CLIENT_SECRET'],
                'userinfo_uri': None,
                'token_introspection_uri': app.config['OIDC_INTROSPECT_URL']
            }
        }
