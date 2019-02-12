# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals


def test_monitoring(client):
    """Test the Prometheus metrics endpoint is working."""
    # First request something even if it doesn't exist to generate a metric
    client.get('/api/v1/story/containeradvisory/123123123?fallback=advisory')
    # Then check the metrics
    rv = client.get('/monitoring/metrics')
    assert rv.status_code == 200
    rv_data = rv.data.decode('utf-8')
    for le in ('0.005', '0.01', '0.025', '0.05', '0.075', '0.1', '0.25', '0.5', '0.75', '1.0',
               '2.5', '5.0', '7.5', '10.0', '+Inf'):
        expected = (
            'request_latency_seconds_bucket{{app_name="estuary-api",endpoint="/api/v1/story/'
            'containeradvisory/123123123",le="{}",query_string="fallback=advisory"}}'.format(le))
        assert expected in rv_data
    expected = ('request_latency_seconds_count{app_name="estuary-api",endpoint="/api/v1/story/'
                'containeradvisory/123123123",query_string="fallback=advisory"}')
    assert expected in rv_data
    expected = ('request_latency_seconds_sum{app_name="estuary-api",endpoint="/api/v1/story/'
                'containeradvisory/123123123",query_string="fallback=advisory"}')
    assert expected in rv_data
