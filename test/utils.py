from models import Player

# Resets the database for testing
def reset_db():
    Player.query.delete()
    # We can add sample users as well