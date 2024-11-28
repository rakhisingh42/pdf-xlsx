from app import create_app, db

# Create an instance of the app and run the database setup inside the app context
app = create_app()

with app.app_context():
    db.create_all()  # Create all tables in the database
    print("Database tables created!")

