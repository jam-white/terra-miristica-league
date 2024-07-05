from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from constants import MAPS, FACTIONS


class AddPlayerForm(FlaskForm):
    name = StringField("Player Name", validators=[DataRequired()])
    submit = SubmitField("Add Player")


class AddFactionForm(FlaskForm):
    name = StringField("Faction Name", validators=[DataRequired()])
    color = StringField("Faction Color (RGB values, e.g. 155, 0, 155)", validators=[DataRequired()])
    submit = SubmitField("Add Faction")


class AddGameForm(FlaskForm):
    bga_id = IntegerField("BGA id (e.g. 359865861)", validators=[DataRequired()])
    num_players = IntegerField("Number of players", validators=[DataRequired(), NumberRange(2,5)])
    round = IntegerField("Round", validators=[DataRequired()])
    group = SelectField("Group", choices=[("A", "A"), ("B", "B"), ("C", "C")], validators=[DataRequired()])
    map = SelectField("Map", choices=MAPS, validators=[DataRequired()])
    p1 = SelectField("Player 1", validators=[DataRequired()])  # Dynamic choices already passed
    p1_faction = SelectField("Player 1 Faction", choices=FACTIONS, validators=[DataRequired()])
    p1_bid = IntegerField("Player 1 Final Bid", validators=[DataRequired(), NumberRange(0, 40)])
    p1_score = IntegerField("Player 1 Final Score", validators=[DataRequired(), NumberRange(0,250)])
    p2 = SelectField("Player 2", validators=[DataRequired()])  # Dynamic choices already passed
    p2_faction = SelectField("Player 2 Faction", choices=FACTIONS, validators=[DataRequired()])
    p2_bid = IntegerField("Player 2 Final Bid", validators=[DataRequired(), NumberRange(0, 40)])
    p2_score = IntegerField("Player 2 Final Score", validators=[DataRequired(), NumberRange(0, 250)])
    p3 = SelectField("Player 3")  # Dynamic choices already passed
    p3_faction = SelectField("Player 3 Faction", choices=([""] + FACTIONS))
    p3_bid = IntegerField("Player 3 Final Bid", validators=[Optional(), NumberRange(0, 40)])
    p3_score = IntegerField("Player 3 Final Score", validators=[Optional(), NumberRange(0, 250)])
    p4 = SelectField("Player 4")  # Dynamic choices already passed
    p4_faction = SelectField("Player 4 Faction", choices=([""] + FACTIONS))
    p4_bid = IntegerField("Player 4 Final Bid", validators=[Optional(), NumberRange(0, 40)])
    p4_score = IntegerField("Player 4 Final Score", validators=[Optional(), NumberRange(0, 250)])
    p5 = SelectField("Player 5")  # Dynamic choices already passed
    p5_faction = SelectField("Player 5 Faction", choices=([""] + FACTIONS))
    p5_bid = IntegerField("Player 5 Final Bid", validators=[Optional(), NumberRange(0, 40)])
    p5_score = IntegerField("Player 5 Final Score", validators=[Optional(), NumberRange(0, 250)])
    submit = SubmitField("Add Game")



