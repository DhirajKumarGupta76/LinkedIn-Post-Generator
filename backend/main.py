from app import create_app, ensure_database_schema

app = create_app()

# Ensure tables exist on cold start (Vercel serverless + local gunicorn).
with app.app_context():
    try:
        ensure_database_schema(app)
    except Exception:
        app.logger.exception('Database schema bootstrap failed')
