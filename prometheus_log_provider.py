import logging
import sys
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway
from datetime import datetime
import uuid
import time

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

    def emit(self, record):
        log_entry = self.format(record)
        timestamp = datetime.utcnow().isoformat()
        unique_id = str(uuid.uuid4())
        self.gauge.labels(unique_id=unique_id, timestamp=timestamp, log_content=log_entry).set(1)
        if record.levelname == 'ERROR':
            self.error_counter.inc()
        self.end_time = datetime.utcnow()
        processing_time = self.end_time - self.start_time
        self.time_taking.set(processing_time.total_seconds())
        push_to_gateway(self.pushgateway_url, job=self.job_name, registry=self.registry)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Set up the handler
# pushgateway_handler = PrometheusPushgatewayHandler('http://3.6.91.242:9091', 'log_collector')
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# pushgateway_handler.setFormatter(formatter)

# # Add the handler to the logger
# logger.addHandler(pushgateway_handler)

# # Redirect print statements to logger
# class PrintLogger:
#     def write(self, message):
#         if message.strip():  # avoid logging empty lines
#             logger.info(message.strip())
#     def flush(self):
#         pass  # This is a no-op to satisfy the interface

# sys.stdout = PrintLogger()

# # Example usage
# print("This is a print statement that should be logged.")
# logger.error("This is an error log message")
# logger.info("This is another info log message")


# import logging
# from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway
# from datetime import datetime
# import uuid
# import time

# class PrometheusPushgatewayHandler(logging.Handler):
#     def __init__(self, pushgateway_url, job_name):
#         super().__init__()
#         self.pushgateway_url = pushgateway_url
#         self.job_name = job_name
#         self.registry = CollectorRegistry()
#         self.gauge = Gauge('log_message', 'Log message with content', ['unique_id', 'timestamp', 'log_content'], registry=self.registry)
#         self.error_counter = Counter('promhttp_metric_handler_errors_total', 'Total number of log errors', registry=self.registry)
#         self.lambda_processing_gauge = Gauge("lambda_processing_time_seconds", 'Description of metric', registry=self.registry)
#         self.logs = []
#         self.start_time = time.time()

#     def emit(self, record):
#         log_entry = self.format(record)
#         timestamp = datetime.utcnow().isoformat()
#         unique_id = str(uuid.uuid4())
#         self.logs.append((unique_id, timestamp, log_entry, record.levelname))
        
#     def push_logs(self):
#         try:
#             print()
#         except:
#             print("Error in push_logs")
#         for unique_id, timestamp, log_content, levelname in self.logs:
#             self.gauge.labels(unique_id=unique_id, timestamp=timestamp, log_content=log_content).set(1)
#             if levelname == 'ERROR':
#                 self.error_counter.inc()
#         end_time = time.time()
#         processing_time = end_time - self.start_time
#         self.lambda_processing_gauge.set(processing_time)
#         push_to_gateway(self.pushgateway_url, job=self.job_name, registry=self.registry)