from app import create_app
from app.auth.models import User, Role, UserRoles
from app.profile import UserProfile
from app.character.models import Character

app, socketio = create_app()

if __name__ == '__main__':
    print("**** Starting the flask app! *****")
    socketio.run(app)


@app.shell_context_processor
def make_shell_context():
    return {
        'User': User,
        'UserProfile': UserProfile,
        'Character': Character,
        'Role': Role,
        'UserRoles': UserRoles
    }
