from werkzeug.security import generate_password_hash, check_password_hash
from models.models import db, User, UserCredential
from repository.user_repository import UserRepository
from schemas.schemas import RegisterSchema, UserSchema, LoginSchema

class UserService:
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.user_schema = UserSchema()
        self.register_schema = RegisterSchema()

    def register_user(self, user_data):
        errors = self.register_schema.validate(user_data)
        if errors:
            return {"errors": errors}, 400
        
        data = self.register_schema.load(user_data)
        
        if self.user_repository.get_by_email(data['name']): 
            return {"error": "El email ya está registrado"}, 400
        
        try:
            new_user = User(
                name=data['name'],
                email=data['email'],
                role=data.get('role', 'student')
            )
            hashed_pw = generate_password_hash(data['password'])
            new_credential = UserCredential(
                password_hash=hashed_pw,
                user=new_user
            )
            db.session.add(new_user)
            db.session.add(new_credential)
            db.session.commit()
            
            return {"message": "Usuario creado con éxito", "user": self.user_schema.dump(new_user)}, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": "Error interno al crear el usuario", "details": str(e)}, 500

    def login_user(self, credentials):
        errors = LoginSchema().validate(credentials)
        if errors:
            return {"errors": errors}, 400
        
        user = self.user_repository.get_by_email(credentials['email'])
        
        if not user or not user.is_active:
            return {"error": "Credenciales inválidas o cuenta desactivada"}, 401
        
        if not check_password_hash(user.credential.password_hash, credentials['password']):
            user.credential.failed_login_attempts += 1
            
            if user.credential.failed_login_attempts >= 5:
                user.is_active = False # bloqueo automatico
                db.session.commit()
                return {"error": "Cuenta bloqueada por demasiados intentos fallidos"}, 403
            
            db.session.commit()
            return {"error": "Credenciales inválidas"}, 401
        
        if user.credential.failed_login_attempts > 0:
            user.credential.failed_login_attempts = 0
            db.session.commit()
        
        return {"message": "Login exitoso", "user": self.user_schema.dump(user)}, 200
    
    def get_all_users(self):
        users = self.user_repository.get_all()
        return UserSchema(many=True).dump(users), 200

    def get_user_by_id(self, user_id):
        user = self.user_repository.get_by_id_or_404(user_id)
        return self.user_schema.dump(user), 200

    def update_profile(self, user_id, update_data):
        user = self.user_repository.get_by_id_or_404(user_id)
        data = UserSchema(partial=True).load(update_data)
        
        for key, value in data.items():
            setattr(user, key, value)
            
        self.user_repository.update()
        return {"message": "Perfil actualizado", "user": self.user_schema.dump(user)}, 200

    def deactivate_user(self, user_id):
        user = self.user_repository.get_by_id_or_404(user_id)
        self.user_repository.soft_delete(user)
        return {"message": "Usuario desactivado correctamente"}, 200