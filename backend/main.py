from app import create_app, ensure_database_schema

app = create_app()

# Ensure tables exist on cold start (Vercel serverless + local run).
with app.app_context():
    try:
        ensure_database_schema(app)
    except Exception:
        app.logger.exception('Database schema bootstrap failed')


if __name__ == '__main__':
    # Local development: keep the process listening on :5000.
    # Vercel imports `main:app` and does not execute this block.
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False),
        use_reloader=False,
    )
