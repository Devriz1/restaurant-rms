from django.db import connection


def run():
    with connection.cursor() as c:
        c.execute("DELETE FROM django_migrations WHERE app='billing' AND name LIKE '0007%'")
        c.execute("DROP TABLE IF EXISTS billing_financialperiod")
        c.execute("DROP TABLE IF EXISTS billing_period")
        c.execute("PRAGMA table_info(billing_bill)")
        cols = [r[1] for r in c.fetchall()]
        # Drop any indexes referencing financial_period_id first
        c.execute("PRAGMA index_list(billing_bill)")
        indexes = c.fetchall()
        for idx in indexes:
            idx_name = idx[1]
            c.execute(f"DROP INDEX IF EXISTS {idx_name}")
        if 'financial_period_id' in cols:
            c.execute("ALTER TABLE billing_bill DROP COLUMN financial_period_id")
        if 'period_id' in cols:
            c.execute("ALTER TABLE billing_bill DROP COLUMN period_id")
    print('cleaned OK')