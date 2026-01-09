from models.models import db, User

class UserRepository:
    
    @staticmethod
    def get_all():
        #para obtener todos los usuarios
        return User.query.all()
    
    @staticmethod
    def get_by_id(user_id):
        #obtiene usuario especifico
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_id_or_404(user_id):
        #si no existe el usuario da error 404
        return User.query.get_or_404(user_id)
    
    @staticmethod
    def get_by_email(email):
        #para el Login y Registro
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def save(user):
        #recibe un objeto User, lo agrega y guarda los cambios
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def delete(user):
        #elimina un usuario de la base de datos
        db.session.delete(user)
        db.session.commit()
    