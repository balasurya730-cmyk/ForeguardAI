import requests

API_URL = 'http://127.0.0.1:8001/api/safety/events'
CLASSES = [
    'PERSON', 'HELMET', 'NO_HELMET', 'GLOVES', 'NO_GLOVES', 'BOOTS', 'NO_BOOTS',
    'GLASSES', 'NO_GLASSES', 'SAFETY_VEST', 'NO_SAFETY_VEST', 'FACE_MASK',
    'FACE_SHIELD', 'MOBILE_PHONE', 'TOOLS', 'MACHINE', 'MACHINE_GUARD',
    'EARMUFFS', 'UNIFORM'
]

success = 0
for cls in CLASSES:
    payload = {
        'camera_id': 1,
        'violation_type': cls,
        'confidence': 0.95,
        'duration_seconds': 2.0
    }
    try:
        res = requests.post(API_URL, json=payload)
        if res.status_code == 200:
            print(f'✅ {cls} - Successfully logged in Backend')
            success += 1
        else:
            print(f'❌ {cls} - Failed: {res.text}')
    except Exception as e:
        print(f'❌ {cls} - Connection error: {e}')

print(f'\nTEST COMPLETE: {success}/{len(CLASSES)} classes verified.')
