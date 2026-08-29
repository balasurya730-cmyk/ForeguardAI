# ForgeGuard AI

**Intelligent Machines. Safer Workers. Secure Factories.**

ForgeGuard AI is a full-stack AI + IoT smart factory monitoring, worker
safety, machine-health and automation platform. It combines machine
health monitoring, worker PPE/helmet safety detection, mobile-phone
detection, gas hazard monitoring, machine runtime control, real-time
alerts, evidence storage, analytics, reports, and a manager/admin
dashboard into one working system.

The entire application runs **without any physical hardware** via a
built-in DEMO MODE, and is architected so real ESP32 sensors (over MQTT)
and a real YOLO camera pipeline can be dropped in later with no code
changes to the backend or frontend.

---

## Architecture

```
ESP32 → MQTT → FastAPI → Database → WebSocket → React
Camera → YOLO → ByteTrack → Rule Engine → FastAPI → WebSocket → React
```

- **Frontend**: React + Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide, native WebSocket
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, JWT auth, WebSocket, MQTT (paho-mqtt)
- **Database**: SQLite for development (swap `DATABASE_URL` for MySQL, no code changes needed)
- **AI**: YOLO (ultralytics) + OpenCV + a lightweight ByteTrack-style tracker, with automatic fallback to a synthetic demo detector when no trained weights are present
- **IoT**: ESP32 + temperature/voltage/current/vibration/gas sensors + relay + buzzer, over MQTT

## Project Structure

```
forgeguard-ai/
├── frontend/       React + Vite dashboard
├── backend/        FastAPI application, database, seed data, tests
├── ai/             YOLO detection, ByteTrack tracking, rule engine
├── iot/esp32/      Arduino sketch for the ESP32 sensor node
├── uploads/        Captured evidence images/videos (served by the backend)
└── README.md
```

---

## Quick Start (Demo Mode — no hardware required)

### 1. Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env
python seed.py                # creates + seeds the SQLite database
uvicorn app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000` (interactive docs at
`http://localhost:8000/docs`). Because `SYSTEM_MODE=DEMO` in `.env`, a
background simulator immediately starts generating realistic sensor, gas,
and worker-safety data — the dashboard will show live-updating values with
no hardware connected.

**Seeded logins:**

| Role     | Email                  | Password       |
|----------|------------------------|----------------|
| Admin    | admin@forgeguard.ai    | Admin@123      |
| Manager  | manager@forgeguard.ai  | Manager@123    |
| Operator | operator@forgeguard.ai | Operator@123   |

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and log in with one of the seeded accounts
above. The Vite dev server proxies `/api`, `/uploads`, and `/ws` to the
backend on port 8000 (see `vite.config.js`), so no CORS configuration is
needed in development.

That's it — you now have machine dashboards, live sensor charts, gas
zones, safety violations, alerts, evidence, analytics, and reports all
populated and updating in real time, entirely in software.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and adjust as needed:

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./forgeguard.db` |
| `JWT_SECRET_KEY` | Secret used to sign JWTs — **change in production** | dev value |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `480` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173,...` |
| `MQTT_BROKER_HOST` / `MQTT_BROKER_PORT` | Broker address (LIVE mode only) | `localhost` / `1883` |
| `MQTT_BASE_TOPIC` | MQTT topic prefix | `forgeguard` |
| `SYSTEM_MODE` | `DEMO` (simulated data) or `LIVE` (real ESP32 + camera) | `DEMO` |
| `UPLOADS_DIR` | Directory served at `/uploads` | `../uploads` |

---

## Database Setup

SQLite is used out of the box — no separate database server is required.
`Base.metadata.create_all()` runs automatically on backend startup, and
`seed.py` populates demonstration data (8 machines, 24 workers, 3 gas
zones, cameras, historical sensor readings, safety events, and alerts).

### Migrating to MySQL

The code uses only standard SQLAlchemy features, so migrating is a
one-line change:

```bash
pip install pymysql
```
```
# backend/.env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/forgeguard
```

Re-run `python seed.py` against the new database (or write your own
migration) — no model or route code needs to change.

---

## AI Setup (Worker Safety Detection)

`ai/detection.py`, `ai/tracking.py`, and `ai/rules.py` implement the full
Camera → YOLO → ByteTrack → Rule Engine → Backend pipeline described in
the architecture diagram above.

- **No trained model?** `Detector` automatically falls back to a
  synthetic-but-plausible detection generator, so the whole pipeline
  (including persistence rules and backend reporting) can be exercised
  end-to-end without a camera or GPU. This is what backs the platform's
  DEMO MODE for safety AI.
- **Have a trained model?** Drop your weights at
  `ai/model/forgeguard_yolo.pt` (see `ai/model/README.md` for training
  notes covering the required classes: `person`, `helmet`, `mobile`,
  `safety_guard`, `PPE`).
- **Run against a real camera:**

  ```bash
  cd ai
  pip install -r requirements.txt
  python -m rules --camera-id 1 --source 0   # 0 = default webcam; or an RTSP URL / video file
  ```

The rule engine applies **persistence logic** — e.g. a helmet must be
missing for several consecutive seconds before a `NO_HELMET` violation is
reported — to avoid false positives from a single noisy frame. Mobile
phone detection is explicitly limited to *visual presence and
persistence*; the system does not claim to infer worker intent.

---

## MQTT Setup (Real IoT Hardware)

1. Run any MQTT broker (e.g. [Mosquitto](https://mosquitto.org/)):
   ```bash
   docker run -it -p 1883:1883 eclipse-mosquitto
   ```
2. Set `SYSTEM_MODE=LIVE` and `MQTT_BROKER_HOST` in `backend/.env`.
3. Restart the backend — it will connect and subscribe to
   `forgeguard/+/sensors` and `forgeguard/+/gas`.

Topics (base topic configurable via `MQTT_BASE_TOPIC`):

| Topic | Direction | Payload |
|---|---|---|
| `forgeguard/<MACHINE_CODE>/sensors` | ESP32 → backend | `{temperature, voltage, current, vibration}` |
| `forgeguard/<MACHINE_CODE>/relay` | backend → ESP32 | `"ON"` / `"OFF"` |
| `forgeguard/<ZONE_NAME>/gas` | ESP32 → backend | `{ppm}` |
| `forgeguard/<ZONE_NAME>/buzzer` | backend → ESP32 | `"ON"` / `"OFF"` |

`machine_code` / `zone_name` must match a `Machine.machine_code` /
`GasZone.zone_name` already present in the database (e.g. from `seed.py`
or created via the dashboard).

## ESP32 Setup

1. Open `iot/esp32/forgeguard.ino` in the Arduino IDE (or PlatformIO).
2. Install libraries: `PubSubClient`, `ArduinoJson`.
3. Edit the configuration block at the top: WiFi credentials, MQTT broker
   IP, `MACHINE_CODE`, `ZONE_NAME`, and pin assignments for your sensors.
4. Flash to an ESP32 dev board wired to: temperature, voltage, current,
   and vibration sensors, a gas sensor, a relay (machine power), and a
   buzzer (gas alarm) — see comments in the sketch for suggested sensor
   models and wiring notes.
5. Calibrate each analog sensor conversion against its datasheet before
   trusting absolute values — the sketch's conversions are illustrative
   placeholders.

## Demo Mode

Demo Mode (`SYSTEM_MODE=DEMO`, the default) is powered by
`backend/app/services/demo_simulator.py`, a background task that:

- Drifts each machine's temperature/voltage/current/vibration smoothly,
  with occasional simulated "spikes" so WARNING/CRITICAL states and
  alerts are demonstrable
- Drifts gas zone ppm levels similarly
- Occasionally emits realistic worker safety violations (helmet, PPE,
  mobile usage) through the same `safety_service.record_violation()` path
  the real AI pipeline uses

Because the simulator calls the *exact same ingestion services* that real
MQTT/AI data would use, switching `SYSTEM_MODE` to `LIVE` requires no
changes to the database schema, API routes, alert engine, or frontend —
only a real MQTT broker and camera/model become the data source instead.

---

## API Documentation

Interactive OpenAPI docs are auto-generated by FastAPI at
`http://localhost:8000/docs` once the backend is running. Key routes:

- **Auth**: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- **Machines**: `GET/POST /api/machines`, `GET/PUT/DELETE /api/machines/{id}`, `GET /api/machines/{id}/readings`
- **Sensors**: `POST /api/sensors/data`
- **Runtime**: `POST /api/machines/{id}/runtime/start|stop`, `GET /api/machines/{id}/runtime`
- **Workers**: `GET /api/workers`, `GET /api/workers/{id}`, `GET /api/workers/{id}/events`
- **Safety**: `GET/POST /api/safety/events`, `GET /api/safety/events/{id}`
- **Evidence**: `GET /api/evidence`, `PUT /api/evidence/{id}/reviewed`
- **Gas**: `GET/POST /api/gas/zones`, `GET/PUT /api/gas/zones/{id}`
- **Alerts**: `GET /api/alerts`, `PUT /api/alerts/{id}/acknowledge|resolve`
- **Reports**: `GET /api/reports/daily|weekly|monthly`
- **Dashboard**: `GET /api/dashboard/summary`, `GET /api/cameras`
- **WebSocket**: `ws://localhost:8000/ws/dashboard` — broadcasts `machine_update`, `gas_update`, `safety_event`, `alert`, and `runtime_update` events

---

## Testing

### Backend

```bash
cd backend
pip install -r requirements.txt pytest httpx
pytest -q
```

Covers authentication, machine CRUD + sensor ingestion, runtime control,
gas threshold rules, and the safety/alert engine (27 tests, all against
an isolated in-memory SQLite database — no shared state with your dev DB).

### Frontend

The frontend is structured so critical flows (login, machine list +
detail, runtime start/stop, alert acknowledge/resolve) are simple,
testable API-driven components. Add `vitest` + `@testing-library/react`
specs under `frontend/src/**/*.test.jsx` as the project grows;
`npm run test` is already wired up via `vitest` in `package.json`.

---

## Deployment Notes

- **Backend**: run behind a production ASGI server (`uvicorn` with
  `--workers`, or `gunicorn -k uvicorn.workers.UvicornWorker`), point
  `DATABASE_URL` at a managed MySQL/Postgres instance, and set a strong
  `JWT_SECRET_KEY`.
- **Frontend**: `npm run build` produces a static `dist/` bundle
  deployable to any static host (Nginx, S3+CloudFront, Vercel, etc.);
  update the API base URL / reverse-proxy rules to point at your deployed
  backend instead of the Vite dev proxy.
- **MQTT**: run a persistent broker (Mosquitto/EMQX) reachable by both the
  backend and your ESP32 devices.
- **Uploads**: mount `uploads/` on persistent storage (or swap for S3/GCS)
  so evidence survives container restarts.

---

## Security

- Passwords are hashed with bcrypt (never stored in plain text)
- JWT bearer tokens with configurable expiry protect all non-auth routes
- Role-based authorization (`ADMIN` / `MANAGER` / `OPERATOR`) restricts
  destructive or configuration actions (creating/editing machines and gas
  zones, runtime control, deleting machines)
- CORS is explicitly configured via `CORS_ORIGINS`
- All request bodies are validated with Pydantic schemas

---

## Development Rules Followed

This build avoids placeholder buttons and fake APIs: every dashboard
value is sourced from the database via a real API call or WebSocket
broadcast, machine health scores are computed from actual sensor readings
(demo-simulated or real), and the AI/IoT modules are structured so demo
and live data flow through identical backend services — no separate
"demo" code path exists downstream of ingestion.
