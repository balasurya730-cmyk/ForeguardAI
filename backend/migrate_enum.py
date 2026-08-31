import sqlite3
conn = sqlite3.connect('forgeguard.db')
c = conn.cursor()
c.execute("UPDATE safety_events SET violation_type = 'PHONE' WHERE violation_type = 'MOBILE_USAGE'")
c.execute("UPDATE safety_events SET violation_type = 'NO_VEST' WHERE violation_type = 'NO_PPE'")
conn.commit()
conn.close()
print('Migration complete.')
