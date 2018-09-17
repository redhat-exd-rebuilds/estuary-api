# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask_oidc import OpenIDConnect


class EstuaryOIDC(OpenIDConnect):
    """Customized version of flask_oidc.OpenIDConnect."""

    def __init__(self, *args, **kwargs):
        """Initialize the EstuaryOIDC class."""
        # Contains a cache of the token information returned by the introspection API endpoint
        self._token_info = {}
        OpenIDConnect.__init__(self, *args, **kwargs)

    def _get_token_info(self, token):
        """
        Request the token information from the introspection API endpoint.

        This wraps the original method to provide a form of caching to avoid calling the
        introspection API endpoint twice if other code needs the decoded JWT.

        :param str token: the access token to get information about
        :return: the token information
        :rtype: dict
        """
        if not self._token_info.get(token):
            self._token_info[token] = OpenIDConnect._get_token_info(self, token)

        return self._token_info[token]

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
