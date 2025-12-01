from django.db import migrations


def add_soccer(apps, schema_editor):
    Sport = apps.get_model("sports", "Sport")
    sports = [
        {"name": "Soccer", "gender": "male"},
        {"name": "Soccer", "gender": "female"},
    ]
    for sport in sports:
        Sport.objects.create(**sport)


def add_soccer_positions(apps, schema_editor):
    Position = apps.get_model("sports", "Position")
    Sport = apps.get_model("sports", "Sport")

    # Soccer position templates
    soccer_positions = [
        {"name": "Goal Keeper", "abbreviation": "GK"},
        {"name": "Right Back", "abbreviation": "RB"},
        {"name": "Left Back", "abbreviation": "LB"},
        {"name": "Center Back", "abbreviation": "CB"},
        {"name": "Sweeper", "abbreviation": "SW"},
        {"name": "Right Midfielder", "abbreviation": "RM"},
        {"name": "Striker", "abbreviation": "S"},
        {"name": "Center Midfielder", "abbreviation": "CM"},
        {"name": "Defensive Midfielder", "abbreviation": "DM"},
        {"name": "Attacking Midfielder", "abbreviation": "AM"},
        {"name": "Right Winger", "abbreviation": "RW"},
        {"name": "Left Winger", "abbreviation": "LW"},
    ]

    positions = []

    # Create positions for both male and female soccer
    for gender in ["male", "female"]:
        sport = Sport.objects.get(name="Soccer", gender=gender)
        for pos in soccer_positions:
            positions.append(
                {
                    "sport": sport,
                    "abbreviation": pos["abbreviation"],
                    "name": pos["name"],
                }
            )

    for position in positions:
        Position.objects.create(**position)


class Migration(migrations.Migration):
    dependencies = [
        ("sports", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_soccer),
        migrations.RunPython(add_soccer_positions),
    ]
