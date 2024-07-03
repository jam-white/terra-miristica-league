from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class AddPlayerForm(FlaskForm):
    name = StringField("Player Name", validators=[DataRequired()])
    submit = SubmitField("Add Player")


class AddFactionForm(FlaskForm):
    name = StringField("Faction Name", validators=[DataRequired()])
    color = StringField("Faction Color", validators=[DataRequired()])
    submit = SubmitField("Add Faction")


class AddGameForm(FlaskForm):
    bga_id = IntegerField("BGA id", validators=[DataRequired()])
    num_players = IntegerField("Number of players", validators=[DataRequired(), NumberRange(2,5)])
    round = IntegerField("Round", validators=[DataRequired()])
    group = SelectField("Group", choices=[("A", "A"), ("B", "B"), ("C", "C")], validators=[DataRequired()])
    map = StringField("Map", validators=[DataRequired()])
    p1 = StringField("Player 1", validators=[DataRequired()])
    p1_faction = StringField("Player 1 Faction", validators=[DataRequired()])
    p1_bid = IntegerField("Player 1 Final Bid", validators=[DataRequired(), NumberRange(0, 40)])
    p1_score = IntegerField("Player 1 Final Score", validators=[DataRequired(), NumberRange(0,250)])
    p2 = StringField("Player 2", validators=[DataRequired()])
    p2_faction = StringField("Player 2 Faction", validators=[DataRequired()])
    p2_bid = IntegerField("Player 2 Final Bid", validators=[DataRequired(), NumberRange(0, 40)])
    p2_score = IntegerField("Player 2 Final Score", validators=[DataRequired(), NumberRange(0, 250)])
    p3 = StringField("Player 3")
    p3_faction = StringField("Player 3 Faction")
    p3_bid = IntegerField("Player 3 Final Bid", validators=[Optional(), NumberRange(0, 40)])
    p3_score = IntegerField("Player 3 Final Score", validators=[Optional(), NumberRange(0, 250)])
    p4 = StringField("Player 4")
    p4_faction = StringField("Player 4 Faction")
    p4_bid = IntegerField("Player 4 Final Bid", validators=[Optional(), NumberRange(0, 40)])
    p4_score = IntegerField("Player 4 Final Score", validators=[Optional(), NumberRange(0, 250)])
    p5 = StringField("Player 5")
    p5_faction = StringField("Player 5 Faction")
    p5_bid = IntegerField("Player 5 Final Bid", validators=[Optional(), NumberRange(0, 40)])
    p5_score = IntegerField("Player 5 Final Score", validators=[Optional(), NumberRange(0, 250)])
    submit = SubmitField("Add Game")



