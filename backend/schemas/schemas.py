from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(attribute="name", dump_only=True) 
    email = fields.Email(dump_only=True)
    role = fields.Str(dump_only=True)
    is_active = fields.Bool()

class RegisterSchema(Schema):
    username = fields.Str(attribute="name", required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    role = fields.Str(validate=validate.OneOf(["student", "instructor", "admin"])) #el rol es opcional, por defecto es student

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)