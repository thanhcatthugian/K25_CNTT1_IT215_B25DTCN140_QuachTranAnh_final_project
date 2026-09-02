from datetime import datetime,timedelta

now = datetime.now()

comp = "2026-12-04"

later = comp < now+timedelta(days=2)

print(later)

