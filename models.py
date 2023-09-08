from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@127.0.0.1:3306/article?autocommit=True'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    category = db.Column(db.String(100))
    created_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    status = db.Column(db.String(100))
