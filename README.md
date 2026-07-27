# To run:
flask run -p 8080

# To send telemetry to a local OpenTelemetry Collector:
# 1. Start the collector
#    docker compose up -d otel-collector
# 2. Run the app with the collector endpoint set
#    OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 flask run -p 8080
#    If you run the app inside Docker, use the collector service name instead:
#    OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318 flask run -p 8080

# To access:
http://localhost:8080/rolldice

# Reference:
https://opentelemetry.io/docs/languages/python/getting-started/#create-and-launch-an-http-server

# Notes:
- If want to test the Zero-Code Instrumentation, make sure to create a separate Python Virtual Environment and install the Packages there.
- Required Python Packages for Zero-Code Instrumentation: `opentelemetry-distro`
- Required command to install the Zero-Code Instrumentation: `opentelemetry-bootstrap -a install`
- Required command to run the App after installing Zero-Code Instrumentation:
opentelemetry-instrument \
    --traces_exporter console \
    --metrics_exporter console \
    --logs_exporter console \
    --service_name dice-server \
    flask run -p 8080

- Required Python Packages for Manual Instrumentation: `opentelemetry-exporter-otlp`
- Then run the Open Telemetry Collector as a Docker Container: docker run -p 4317:4317 \
    -v /tmp/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
    otel/opentelemetry-collector:latest \
    --config=/etc/otel-collector-config.yaml


