import datetime
import hashlib
import json
from peewee import (
    SqliteDatabase, Model, CharField, TextField, IntegerField,
    FloatField, BooleanField, DateTimeField, ForeignKeyField,
)
from config import DATABASE_PATH

db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Source(BaseModel):
    name = CharField(unique=True)
    source_type = CharField()  # rss, scraper, newsapi, rsshub
    url = TextField()
    config = TextField(default="{}")
    enabled = BooleanField(default=True)
    fetch_interval_minutes = IntegerField(default=60)
    last_fetched_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)


class Article(BaseModel):
    source = ForeignKeyField(Source, backref="articles")
    url = TextField()
    url_hash = CharField(max_length=64, unique=True)
    title = TextField()
    summary_raw = TextField(null=True)
    content_raw = TextField(null=True)
    author = CharField(null=True)
    published_at = DateTimeField(null=True)
    fetched_at = DateTimeField(default=datetime.datetime.now)

    region = CharField(null=True, index=True)
    carrier = CharField(null=True, index=True)  # FedEx, UPS, Both, Other
    route_type = CharField(null=True, index=True)  # new_route, route_change, intercontinental, general
    keywords = TextField(null=True)

    analysis_status = CharField(default="pending")  # pending, processing, done, skipped
    ai_summary_cn = TextField(null=True)
    extracted_routes = TextField(null=True)
    analyzed_at = DateTimeField(null=True)

    is_read = BooleanField(default=False)
    is_flagged = BooleanField(default=False)

    class Meta:
        indexes = (
            (("published_at", "analysis_status"), False),
            (("carrier", "region"), False),
        )


class RouteChange(BaseModel):
    article = ForeignKeyField(Article, backref="route_changes")
    origin = CharField()
    destination = CharField()
    action = CharField()  # new, resumed, suspended, increased_freq, decreased_freq, aircraft_change
    effective_date = DateTimeField(null=True)
    aircraft_type = CharField(null=True)
    confidence = FloatField(default=0.0)
    created_at = DateTimeField(default=datetime.datetime.now)


class Notification(BaseModel):
    article = ForeignKeyField(Article, null=True, backref="notifications")
    title = CharField()
    body = TextField()
    notification_type = CharField()  # new_route, intercontinental_change, daily_digest
    sent_at = DateTimeField(null=True)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)


def url_to_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def init_db():
    db.init(DATABASE_PATH, pragmas={
        "journal_mode": "wal",
        "foreign_keys": 1,
    })
    db.connect()
    db.create_tables([Source, Article, RouteChange, Notification], safe=True)
    return db
