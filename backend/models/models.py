from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) #con lambda se actualiza en cada cambio
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True) 
    role = db.Column(db.String(20), default='student')


class UserCredential(db.Model):
    __tablename__ = 'user_credentials'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id"), 
        unique=True, 
        nullable=False
    )
    password_hash = db.Column(db.String(512), nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False) #esto cuenta cuantas veces falló el login seguido
    user = db.relationship(
        "User", 
        backref=db.backref("credential", uselist=False)
    )
 
    
class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2), default=0.00)
    instructor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    category_id = db.Column(
        db.Integer, 
        db.ForeignKey("categories.id"), 
        nullable=False
    )    
    is_published = db.Column(db.Boolean, default=False)
    level_difficulty = db.Column(db.String(20), nullable=False, default="principiante")    
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) #con lambda se actualiza en cada cambio
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True) 
    lessons = db.relationship(
        'Lesson', 
        backref='course', 
        lazy=True, 
        cascade="all, delete-orphan"
    ) #para acceder a las lecciones facilmente
    
    
class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=True) 
    video_url = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, nullable=False, default=1)
    course_id = db.Column(
        db.Integer, 
        db.ForeignKey('courses.id'), 
        nullable=False
    ) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)   
    __table_args__ = (
        db.UniqueConstraint('course_id', 'order', name='unique_lesson_order_per_course'),
    ) #esto asegura que no pueda existir una "Lección 1" duplicada para un mismo curso 
     
    #no es necesario declarar la relacion de cursos con leccion 
    #porque ya esta creada en la tabla lecciones

    
class Enrollment(db.Model): #inscripciones
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )
    enrollment_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    progress_percent = db.Column(db.Integer, default=0)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='unique_user_course_enrollment'),
    ) #para evitar inscripciones duplicadas
    user = db.relationship(
        "User",
        backref=db.backref("enrollments", lazy=True)
    )
    course = db.relationship(
        "Course", 
        backref=db.backref("enrollments", lazy=True)
    )
 
    
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    courses = db.relationship(
        'Course', 
        backref='category', 
        lazy=True
    )
    def __repr__(self):
        return f'<Category {self.name}>'
    

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False) #de 1 a 5 estrellas
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        nullable=False
    )
    course_id = db.Column(
        db.Integer, 
        db.ForeignKey('courses.id'), 
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='unique_user_rating_per_course'), 
    ) #esto sirve como restriccion para que un usuario solo pueda calificar un curso una vez
    user = db.relationship(
        "User", 
        backref=db.backref("ratings", lazy=True)
    )
    course = db.relationship(
        "Course", 
        backref=db.backref("ratings", lazy=True)
    )