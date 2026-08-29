/*
 * ForgeGuard AI — ESP32 IoT Node
 * -------------------------------
 * Reads machine sensors (temperature, voltage, current, vibration) and an
 * optional gas sensor, publishes readings over MQTT, and listens for
 * relay (machine runtime) and buzzer (gas alarm) commands from the
 * ForgeGuard backend.
 *
 * MQTT topics (base topic configurable, default "forgeguard"):
 *   Publish:
 *     forgeguard/<MACHINE_CODE>/sensors   JSON: {temperature, voltage, current, vibration}
 *     forgeguard/<ZONE_NAME>/gas          JSON: {ppm}
 *   Subscribe:
 *     forgeguard/<MACHINE_CODE>/relay     payload: "ON" | "OFF"
 *     forgeguard/<ZONE_NAME>/buzzer       payload: "ON" | "OFF"
 *
 * Hardware:
 *   - ESP32 dev board
 *   - Temperature sensor (e.g. DS18B20 or analog LM35) -> TEMP_PIN
 *   - Voltage sensor module (e.g. ZMPT101B)             -> VOLTAGE_PIN
 *   - Current sensor (e.g. ACS712)                      -> CURRENT_PIN
 *   - Vibration sensor (e.g. SW-420 or ADXL345 analog)  -> VIBRATION_PIN
 *   - Gas sensor (e.g. MQ-2 / MQ-6, calibrated per gas)  -> GAS_PIN
 *   - Relay module (machine power control)               -> RELAY_PIN
 *   - Buzzer (gas alarm)                                 -> BUZZER_PIN
 *
 * NOTE: The analog->physical-unit conversions below are simplified/
 * illustrative. Calibrate each sensor against its datasheet and your
 * specific hardware before relying on absolute values in production.
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ---------------- Configuration ----------------
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

const char* MQTT_BROKER_HOST = "192.168.1.100";  // your MQTT broker IP
const int   MQTT_BROKER_PORT = 1883;
const char* MQTT_USERNAME = "";                  // leave blank if not used
const char* MQTT_PASSWORD = "";

const char* BASE_TOPIC = "forgeguard";
const char* MACHINE_CODE = "MOTOR-01";           // must match a seeded Machine.machine_code
const char* ZONE_NAME = "ZONE A";                // must match a seeded GasZone.zone_name

const unsigned long PUBLISH_INTERVAL_MS = 3000;

// ---------------- Pin assignments ----------------
const int TEMP_PIN = 34;
const int VOLTAGE_PIN = 35;
const int CURRENT_PIN = 32;
const int VIBRATION_PIN = 33;
const int GAS_PIN = 36;
const int RELAY_PIN = 25;
const int BUZZER_PIN = 26;

// ---------------- Globals ----------------
WiFiClient espClient;
PubSubClient mqttClient(espClient);
unsigned long lastPublish = 0;

char relayTopic[64];
char buzzerTopic[64];
char sensorsTopic[64];
char gasTopic[64];

void connectWifi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.println(" connected.");
  Serial.println(WiFi.localIP());
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) message += (char)payload[i];
  message.trim();

  Serial.printf("MQTT message on %s: %s\n", topic, message.c_str());

  if (strcmp(topic, relayTopic) == 0) {
    digitalWrite(RELAY_PIN, message == "ON" ? HIGH : LOW);
  } else if (strcmp(topic, buzzerTopic) == 0) {
    digitalWrite(BUZZER_PIN, message == "ON" ? HIGH : LOW);
  }
}

void connectMqtt() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT broker...");
    String clientId = "esp32-" + String(MACHINE_CODE);
    bool ok;
    if (strlen(MQTT_USERNAME) > 0) {
      ok = mqttClient.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD);
    } else {
      ok = mqttClient.connect(clientId.c_str());
    }

    if (ok) {
      Serial.println(" connected.");
      mqttClient.subscribe(relayTopic);
      mqttClient.subscribe(buzzerTopic);
    } else {
      Serial.printf(" failed, rc=%d. Retrying in 2s\n", mqttClient.state());
      delay(2000);
    }
  }
}

// ---------------- Sensor reads (calibrate for your hardware) ----------------
float readTemperature() {
  int raw = analogRead(TEMP_PIN);
  // Example linear approximation for an LM35-style analog sensor on a
  // 3.3V ADC; replace with your sensor's proper conversion / library.
  float voltage = raw * (3.3 / 4095.0);
  return voltage * 100.0;  // degrees C
}

float readVoltage() {
  int raw = analogRead(VOLTAGE_PIN);
  float sensorVoltage = raw * (3.3 / 4095.0);
  return sensorVoltage * 100.0;  // scaled to mains voltage range, calibrate to your ZMPT101B
}

float readCurrent() {
  int raw = analogRead(CURRENT_PIN);
  float sensorVoltage = raw * (3.3 / 4095.0);
  float offsetVoltage = 1.65;  // ACS712 zero-current midpoint
  float sensitivity = 0.185;   // V per A, for ACS712-05B; adjust for your module
  return (sensorVoltage - offsetVoltage) / sensitivity;
}

float readVibration() {
  int raw = analogRead(VIBRATION_PIN);
  return (raw / 4095.0) * 10.0;  // scaled to an illustrative mm/s range
}

float readGasPpm() {
  int raw = analogRead(GAS_PIN);
  // MQ-series sensors need a proper Rs/R0 curve for accurate ppm; this is
  // a simplified linear placeholder — calibrate against your specific gas
  // and sensor model before using in a safety-critical setting.
  return (raw / 4095.0) * 1000.0;
}

void publishSensorData() {
  StaticJsonDocument<200> doc;
  doc["temperature"] = readTemperature();
  doc["voltage"] = readVoltage();
  doc["current"] = readCurrent();
  doc["vibration"] = readVibration();

  char buffer[200];
  size_t len = serializeJson(doc, buffer);
  mqttClient.publish(sensorsTopic, buffer, len);

  StaticJsonDocument<64> gasDoc;
  gasDoc["ppm"] = readGasPpm();
  char gasBuffer[64];
  size_t gasLen = serializeJson(gasDoc, gasBuffer);
  mqttClient.publish(gasTopic, gasBuffer, gasLen);

  Serial.printf("Published sensors: %s | gas: %s\n", buffer, gasBuffer);
}

void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  snprintf(sensorsTopic, sizeof(sensorsTopic), "%s/%s/sensors", BASE_TOPIC, MACHINE_CODE);
  snprintf(relayTopic, sizeof(relayTopic), "%s/%s/relay", BASE_TOPIC, MACHINE_CODE);
  snprintf(gasTopic, sizeof(gasTopic), "%s/%s/gas", BASE_TOPIC, ZONE_NAME);
  snprintf(buzzerTopic, sizeof(buzzerTopic), "%s/%s/buzzer", BASE_TOPIC, ZONE_NAME);

  connectWifi();
  mqttClient.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
  mqttClient.setCallback(onMqttMessage);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWifi();
  }
  if (!mqttClient.connected()) {
    connectMqtt();
  }
  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_INTERVAL_MS) {
    lastPublish = now;
    publishSensorData();
  }
}
