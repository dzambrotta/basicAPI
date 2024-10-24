import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nbaPlayers.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "team": self.team,
            "position": self.position,
            "height": self.height,
            "weight": self.weight,
            "created_at": self.created_at.isoformat(),
        }


@app.route("/api/players", methods=["GET"])
def get_players():
    players = Player.query.all()
    return jsonify([player.to_dict() for player in players])


@app.route("/api/players/<string:name>", methods=["GET"])
def get_player(name):
    player = Player.query.filter(Player.name == name).first_or_404()
    return jsonify(player.to_dict())


# create player
@app.route("/api/players", methods=["POST"])
def create_player():
    try:
        new_player = Player(
            name=request.json["name"],
            team=request.json["team"],
            position=request.json["position"],
            height=request.json["height"],
            weight=request.json["weight"],
        )
        db.session.add(new_player)
        db.session.commit()

        return jsonify(new_player.to_dict())
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400


# delete player
@app.route("/api/players/<string:name>", methods=["DELETE"])
def del_player(name):
    player = Player.query.filter(Player.name == name).first_or_404()
    db.session.delete(player)
    db.session.commit()
    return "", 204


# update player
@app.route("/api/players/<string:name>", methods=["PUT"])
def update_player(name):
    player = Player.query.filter(Player.name == name).first_or_404()

    if "name" in request.json:
        player.name = request.json["name"]
    if "team" in request.json:
        player.team = request.json["team"]
    if "position" in request.json:
        player.position = request.json["position"]
    if "height" in request.json:
        player.height = request.json["height"]
    if "weight" in request.json:
        player.weight = request.json["weight"]

    db.session.commit()
    return jsonify(player.to_dict())


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port="5001")
