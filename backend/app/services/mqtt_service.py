"""
MQTT integration for real ESP32 hardware.

Topics (base = settings.MQTT_BASE_TOPIC, default "forgeguard"):
  {base}/{machine_code}/sensors   <- ESP32 publishes JSON sensor payload
  {base}/{machine_code}/relay     -> backend publishes "ON"/"OFF"
  {base}/{zone_name}/gas          <- ESP32 publishes gas ppm
  {base}/{zone_name}/buzzer       -> backend publishes "ON"/"OFF"

In DEMO mode the client is never started; publish_relay_command() and
publish_buzzer_command() simply log instead of touching a real broker,
so the rest of the app can call them unconditionally.
"""
import asyncio
import json
import logging
import threading

from app.config import settings

logger = logging.getLogger("forgeguard.mqtt")

_client = None
_main_loop: asyncio.AbstractEventLoop | None = None


def _on_message(client, userdata, msg):
    """Runs on the paho network thread; hand off to the asyncio loop."""
    if _main_loop is None:
        return
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        logger.warning("Could not decode MQTT payload on %s", msg.topic)
        return

    from app.services.mqtt_handlers import handle_incoming_message
    asyncio.run_coroutine_threadsafe(handle_incoming_message(msg.topic, payload), _main_loop)


def start_mqtt_client(loop: asyncio.AbstractEventLoop):
    """Connect to the broker and subscribe to sensor/gas topics. Only called
    when SYSTEM_MODE=LIVE; safe to skip entirely in DEMO mode."""
    global _client, _main_loop
    if settings.SYSTEM_MODE != "LIVE":
        logger.info("SYSTEM_MODE=DEMO: MQTT client not started (using built-in simulator instead).")
        return

    import paho.mqtt.client as mqtt

    _main_loop = loop
    _client = mqtt.Client()
    if settings.MQTT_USERNAME:
        _client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    _client.on_message = _on_message

    try:
        _client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=30)
        _client.subscribe(f"{settings.MQTT_BASE_TOPIC}/+/sensors")
        _client.subscribe(f"{settings.MQTT_BASE_TOPIC}/+/gas")
        thread = threading.Thread(target=_client.loop_forever, daemon=True)
        thread.start()
        logger.info("MQTT client connected to %s:%s", settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
    except Exception as exc:
        logger.error("MQTT connection failed (%s). Falling back to demo simulator behaviour.", exc)


def publish_relay_command(machine_code: str, state: str):
    topic = f"{settings.MQTT_BASE_TOPIC}/{machine_code}/relay"
    if _client is None:
        logger.info("[DEMO] Would publish relay command %s -> %s", topic, state)
        return
    _client.publish(topic, state)


def publish_buzzer_command(zone_name: str, state: str):
    topic = f"{settings.MQTT_BASE_TOPIC}/{zone_name}/buzzer"
    if _client is None:
        logger.info("[DEMO] Would publish buzzer command %s -> %s", topic, state)
        return
    _client.publish(topic, state)
