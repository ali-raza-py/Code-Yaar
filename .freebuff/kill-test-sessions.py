import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection

with connection.cursor() as cur:
    cur.execute(
        "SELECT pid, state, query FROM pg_stat_activity WHERE datname = 'test_postgres'"
    )
    rows = cur.fetchall()
    print("sessions:", rows)
    for pid, *_ in rows:
        cur.execute("SELECT pg_terminate_backend(%s)", [pid])
        print("terminated", pid, "->", cur.fetchone())
