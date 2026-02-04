from app.root_legacy.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

# Gunicorn entrypoint
app = create_app()

