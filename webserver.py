"""Compatibility entrypoint for Angel2500 AI Core v5."""
from angel2500.app import create_app

app = create_app()

if __name__ == "__main__":
    import os
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "8080")), debug=False)
