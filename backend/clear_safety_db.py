import sqlite3
conn = sqlite3.connect('forgeguard.db')
c = conn.cursor()
c.execute("DELETE FROM safety_events")
c.execute("DELETE FROM evidence")
c.execute("DELETE FROM alerts WHERE alert_type NOT IN ('HIGH_TEMPERATURE', 'HIGH_VOLTAGE', 'HIGH_CURRENT', 'HIGH_VIBRATION', 'GAS_WARNING', 'GAS_CRITICAL', 'MACHINE_RUNTIME_COMPLETE', 'MACHINE_OFFLINE')")
conn.commit()
conn.close()
print('Database cleared of old safety data.')
