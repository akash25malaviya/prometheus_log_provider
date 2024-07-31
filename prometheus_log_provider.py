import logging
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway
from opentelemetry.trace import set_span_in_context
from datetime import datetime
import uuid
import sys

# class PrometheusPushgatewayHandler(logging.Handler):
#     def __init__(self, pushgateway_url, job_name):
#         super().__init__()
#         self.pushgateway_url = pushgateway_url
#         self.job_name = job_name
#         self.registry = CollectorRegistry()
#         self.gauge = Gauge('log_message', 'Log message with content', ['unique_id', 'timestamp', 'log_content'], registry=self.registry)
#         self.error_counter = Counter('promhttp_metric_handler_errors_total', 'Total number of log errors', registry=self.registry)
#         self.time_taking = Gauge("lambda_processing_time_seconds", 'Description of metric', registry=self.registry)
#         self.start_time = datetime.utcnow()
#         self.end_time = datetime.utcnow()

#     def emit(self, record):
#         log_entry = self.format(record)
#         timestamp = datetime.utcnow().isoformat()
#         unique_id = str(uuid.uuid4())
#         self.gauge.labels(unique_id=unique_id, timestamp=timestamp, log_content=log_entry).set(1)
#         if record.levelname == 'ERROR':
#             self.error_counter.inc()
#         self.end_time = datetime.utcnow()
#         processing_time = self.end_time - self.start_time
#         self.time_taking.set(processing_time.total_seconds())
#         push_to_gateway(self.pushgateway_url, job=self.job_name, registry=self.registry)



class PrometheusPushgatewayHandler(logging.Handler):
    def __init__(self, pushgateway_url, job_name):
        super().__init__()
        self.pushgateway_url = pushgateway_url
        self.job_name = job_name
        self.registry = CollectorRegistry()
        self.gauge = Gauge('log_message', 'Log message with content', ['unique_id', 'timestamp', 'log_content'], registry=self.registry)
        self.error_counter = Counter('promhttp_metric_handler_errors_total', 'Total number of log errors', registry=self.registry)
        self.time_taking = Gauge("lambda_processing_time_seconds", 'Description of metric', registry=self.registry)
        self.start_time = datetime.utcnow()
        self.end_time = datetime.utcnow()

        # Initialize Jaeger Tracer
        self.jaeger_host = "65.0.134.216"
        self.jaeger_port = 6831
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.info(f'Initializing Jaeger Exporter with host: {self.jaeger_host}, port: {self.jaeger_port}')
        self.jaeger_exporter = JaegerExporter(
            agent_host_name=self.jaeger_host,
            agent_port=self.jaeger_port,
        )
        self.resource = Resource.create({"service.name": self.job_name})
        self.provider = TracerProvider(resource=self.resource)
        trace.set_tracer_provider(self.provider)
        self.span_processor = BatchSpanProcessor(self.jaeger_exporter)
        self.provider.add_span_processor(self.span_processor)
        self.logger.info('Jaeger Exporter initialized successfully')

        # Start a root span for the whole session
        self.tracer = self.provider.get_tracer(__name__)
        self.root_span = self.tracer.start_span("log_session")
        self.root_context = set_span_in_context(self.root_span)

        # Initialize last log entry storage
        self.last_log_entry = None

        # Track if shutdown has been called
        self._shutdown_called = False

    def emit(self, record):
        if self._shutdown_called:
            return

        log_entry = self.format(record)
        self.last_log_entry = log_entry  # Store the current log entry

        timestamp = datetime.utcnow().isoformat()
        unique_id = str(uuid.uuid4())
        self.gauge.labels(unique_id=unique_id, timestamp=timestamp, log_content=log_entry).set(1)
        if record.levelname == 'ERROR':
            self.error_counter.inc()
        self.end_time = datetime.utcnow()
        processing_time = self.end_time - self.start_time
        self.time_taking.set(processing_time.total_seconds())

        # Create a span for this log entry within the root context
        with self.tracer.start_span("log_entry_handler", context=self.root_context) as span:
            span.set_attribute("log_message", log_entry)  # Set the log entry
            span.set_attribute("timestamp", timestamp)
            span.set_attribute("unique_id", unique_id)

            # Push metrics to Prometheus Pushgateway
            push_to_gateway(self.pushgateway_url, job=self.job_name, registry=self.registry)

    def shutdown(self):
        if not self._shutdown_called:
            self._shutdown_called = True
            # End the root span
            self.root_span.end()

            # Shutdown Jaeger Tracer and associated components
            self.provider.shutdown()

    def close(self):
        # Ensure proper cleanup when handler is closed
        super().close()
        self.shutdown()

    def __del__(self):
        # Ensure shutdown on object destruction
        self.shutdown()







# class PrometheusPushgatewayHandler(logging.Handler):
#     def __init__(self, pushgateway_url, job_name):
#         super().__init__()
#         self.pushgateway_url = pushgateway_url
#         self.job_name = job_name
#         self.registry = CollectorRegistry()
#         self.gauge = Gauge('log_message', 'Log message with content', ['unique_id', 'timestamp', 'log_content'], registry=self.registry)
#         self.error_counter = Counter('promhttp_metric_handler_errors_total', 'Total number of log errors', registry=self.registry)
#         self.time_taking = Gauge("lambda_processing_time_seconds", 'Description of metric', registry=self.registry)
#         self.start_time = datetime.utcnow()
#         self.end_time = datetime.utcnow()

#         # Initialize Jaeger Tracer
#         self.jaeger_host = "65.0.134.216"
#         self.jaeger_port = 6831
#         self.logger = logging.getLogger()
#         self.logger.setLevel(logging.INFO)
#         self.logger.info(f'Initializing Jaeger Exporter with host: {self.jaeger_host}, port: {self.jaeger_port}')
#         self.jaeger_exporter = JaegerExporter(
#             agent_host_name=self.jaeger_host,
#             agent_port=self.jaeger_port,
#         )
#         self.resource = Resource.create({"service.name": self.job_name})
#         self.provider = TracerProvider(resource=self.resource)
#         trace.set_tracer_provider(self.provider)
#         self.span_processor = BatchSpanProcessor(self.jaeger_exporter)
#         self.provider.add_span_processor(self.span_processor)
#         self.logger.info('Jaeger Exporter initialized successfully')

#     def emit(self, record):
#         log_entry = self.format(record)
#         timestamp = datetime.utcnow().isoformat()
#         unique_id = str(uuid.uuid4())
#         self.gauge.labels(unique_id=unique_id, timestamp=timestamp, log_content=log_entry).set(1)
#         if record.levelname == 'ERROR':
#             self.error_counter.inc()
#         self.end_time = datetime.utcnow()
#         processing_time = self.end_time - self.start_time
#         self.time_taking.set(processing_time.total_seconds())

#         # Start Jaeger span
#         tracer = self.provider.get_tracer(__name__)
#         with tracer.start_as_current_span("lambda_handler"):
#             span = trace.get_current_span()
#             span.set_attribute("log_message", log_entry)
#             span.set_attribute("timestamp", timestamp)
#             span.set_attribute("unique_id", unique_id)

#         # Push metrics to Prometheus Pushgateway
#         push_to_gateway(self.pushgateway_url, job=self.job_name, registry=self.registry)

#         # Shutdown Jaeger Tracer
#         self.provider.shutdown()