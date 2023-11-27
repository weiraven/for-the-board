from models import User

# Resets the database for testing
def reset_db():
    User.query.delete()
    # We can add sample users as well