from app import create_app, ensure_database_schema

app = create_app()


with app.app_context():
    ensure_database_schema(app)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
