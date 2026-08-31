import sqlite3
conn = sqlite3.connect('forgeguard.db')
c = conn.cursor()
c.execute("UPDATE alerts SET alert_type = 'PHONE' WHERE alert_type = 'MOBILE_USAGE'")
c.execute("UPDATE alerts SET alert_type = 'NO_VEST' WHERE alert_type = 'NO_PPE'")
conn.commit()
conn.close()
print('Alerts Migration complete.')
