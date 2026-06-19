import os
import sys
from flask import Flask
from config import BASE_DIR
def create_app() -> Flask:
    app = Flask(__name__)

    data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)

    from models import db, Source, Article, RouteChange, Notification
    db.init(os.path.join(data_dir, "mynewsavi.db"), pragmas={
        "journal_mode": "wal",
        "foreign_keys": 1,
    })
    db.connect()
    db.create_tables([Source, Article, RouteChange, Notification], safe=True)

    from web.main import main_bp
    from web.archive import archive_bp
    from web.api import api_bp
    from web.reference import reference_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(archive_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(reference_bp)

    # Start scheduler immediately on startup
    try:
        from scheduler import start_scheduler
        start_scheduler()
        print("[Scheduler] Background scheduler started.", file=sys.stderr)
    except Exception as e:
        print(f"[Scheduler] Failed to start: {e}", file=sys.stderr)

    return app


if __name__ == "__main__":
    app = create_app()
    print("MyNewsAVI starting at http://localhost:8080", file=sys.stderr)
    app.run(debug=False, host="0.0.0.0", port=8080)
