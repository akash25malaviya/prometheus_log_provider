# Overview
PrometheusPushgatewayHandler is a custom logging handler designed to push log messages and various metrics to a Prometheus Pushgateway. It extends the Python logging.Handler class to integrate with Prometheus metrics, allowing you to monitor and alert based on log data and other application-specific metrics.

# Features
Push log messages to Prometheus Pushgateway with unique identifiers and timestamps.
Count the total number of log errors.
Measure and record the time taken for processing logs.
Easily integrate with existing Python logging setups.
Installation
# To use the PrometheusPushgatewayHandler, you need to install the following Python packages:
pip install prometheus_client

# Configuration
pushgateway_url: URL of the Prometheus Pushgateway.
job_name: Name of the job under which metrics will be grouped.
# Metrics
log_message: Gauge metric to store log messages with unique identifiers and timestamps.
promhttp_metric_handler_errors_total: Counter metric to count the total number of log errors.
lambda_processing_time_seconds: Gauge metric to measure the time taken for processing logs.


# Example usage
logger = logging.getLogger('prometheus_logger')
pushgateway_url = 'http://your-pushgateway-url:9091'
job_name = 'your_job_name'
prom_handler = PrometheusPushgatewayHandler(pushgateway_url, job_name)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
prom_handler.setFormatter(formatter)

logger.addHandler(prom_handler)
logger.setLevel(logging.INFO)

# Log some messages
logger.info('This is an info message')
logger.error('This is an error message')
