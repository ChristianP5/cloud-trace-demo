import os
from random import randint
from flask import Flask, request
import logging

# Import and Set Up Tracer START
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

resource = Resource.create(attributes={
    SERVICE_NAME: "dice-roller-service",
})

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

tracerProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces"))
tracerProvider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(tracerProvider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.name")

# Import and Set Up Tracer END

# Import and Set Up Metrics START
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=f"{otlp_endpoint}/v1/metrics")
)
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

# Creates a meter from the global meter provider
meter = metrics.get_meter("my.meter.name")

# Import and Set Up Metrics END

# Import and Set Up Logging START
import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogRecordExporter # ConsoleLogExporter on versions earlier than 1.39.0
from opentelemetry._logs import set_logger_provider

provider = LoggerProvider()
processor = BatchLogRecordProcessor(ConsoleLogRecordExporter())
provider.add_log_record_processor(processor)
# Sets the global default logger provider
set_logger_provider(provider)

handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
logging.basicConfig(handlers=[handler], level=logging.INFO)

logging.getLogger(__name__).info("This is an OpenTelemetry log record!")
# Import and Set Up Logging END

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/rolldice")
def roll_dice():
    with tracer.start_as_current_span("GET /rolldice") as span:
        current_span = trace.get_current_span()
        current_span.set_attribute(SpanAttributes.HTTP_METHOD, "GET")

        logging.getLogger(__name__).info("Simulating some processing time")
        sleep(0.5)  # Simulate some processing time
        player = request.args.get('player', default=None, type=str)
        result = str(roll())
        if player:
            logger.warning("%s is rolling the dice: %s", player, result)
        else:
            logger.warning("Anonymous player is rolling the dice: %s", result)
        return result


def roll():
    logging.getLogger(__name__).info("Starting to roll the dice")
    with tracer.start_as_current_span("roll()") as span:
        res = randint(1, 6)
        span.set_attribute("roll.value", res)
        return res

@tracer.start_as_current_span("sleep()")
def sleep(seconds):
    logging.getLogger(__name__).info(f"Simulating a sleep for {seconds} seconds")
    import time
    current_span = trace.get_current_span()
    current_span.add_event(f"Started sleeping for {seconds} seconds")

    time.sleep(seconds)

    current_span.add_event(f"Finished sleeping for {seconds} seconds")
    logging.getLogger(__name__).info("Finished sleeping!")

@tracer.start_as_current_span("simulate_error()")
def simulate_error():
    logging.getLogger(__name__).info("Simulating an error with an exception")
    import time
    current_span = trace.get_current_span()
    current_span.add_event(f"Started simulating error")

    try:
        time.sleep(1)
        raise Exception("Simulated error")
    except Exception as ex:
        current_span.set_status(Status(StatusCode.ERROR))
        current_span.record_exception(ex)

    current_span.add_event(f"Finished simulating error with an exception")
    logging.getLogger(__name__).info("Finished simulating error with an exception")


app.run(host='0.0.0.0', port=8080, debug=True)