import enum
from datetime import datetime, timedelta

import jwt
from decouple import config
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jwt import DecodeError, InvalidSignatureError
from sqlalchemy import func
from marshmallow import Schema, fields, validate, ValidationError, validates
from password_strength import PasswordPolicy
from werkzeug.exceptions import BadRequest, InternalServerError, Forbidden
from werkzeug.security import generate_password_hash
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config("DB_USERNAME")}:{config("DB_PASSWORD")}' \
                                        f'@localhost:{config("DB_PORT")}/{config("DB_NAME")}'

db = SQLAlchemy(app)
api = Api(app)
migrate = Migrate(app, db)

auth = HTTPTokenAuth(scheme='Bearer')


def validate_schemas(schema_name):
    def decorator_func(func_):
        def wrapper(*args, **kwargs):
            data = request.get_json()
            schema = schema_name()
            errors = schema.validate(data)
            if errors:
                raise BadRequest(errors)
            return func_(*args, **kwargs)

        return wrapper

    return decorator_func


def permission_required(permission_level):
    if not isinstance(permission_level, list):
        permission_level = [permission_level]

    def decorator_func(func_):
        def wrapper(*args, **kwargs):
            if auth.current_user().role in permission_level:
                return func_(*args, **kwargs)
            raise Forbidden('you have no permission to access this')

        return wrapper

    return decorator_func


@auth.verify_token
def verify_token(token):
    token_decode_data = User.decode_token(token)
    user = User.query.filter_by(id=token_decode_data["sub"]).first()
    return user


users_clothes = db.Table(
    "users_clothes",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("clothes_id", db.Integer, db.ForeignKey("clothes.id")),
)


class UserRoles(enum.Enum):
    super_admin = 'super admin'
    admin = 'admin'
    user = 'user'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Text)
    role = db.Column(db.Enum(UserRoles), server_default=UserRoles.user.name, nullable=False)
    create_on = db.Column(db.DateTime, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())

    # clothes = db.relationship("Clothes", secondary=users_clothes)

    def encode_token(self):
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(hours=8),
                'sub': self.id
            }
            return jwt.encode(
                payload,
                key=config('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_token(token):
        try:
            return jwt.decode(token, key=config('SECRET_KEY'), algorithms=['HS256'])
        except (DecodeError, InvalidSignatureError) as de:
            raise BadRequest('Invalid or missing token')
        except Exception as e:
            raise InternalServerError('Something went wrong')


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"


class Clothes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    color = db.Column(
        db.Enum(ColorEnum),
        default=ColorEnum.white,
        nullable=False
    )
    size = db.Column(
        db.Enum(SizeEnum),
        default=SizeEnum.s,
        nullable=False
    )
    photo = db.Column(db.String(255), nullable=False)
    create_on = db.Column(db.DateTime, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())


def validate_name(value):
    try:
        first_name, last_name = value.split()
    except ValueError as e:
        raise ValidationError('Invalid name! Expected two names')


policy = PasswordPolicy.from_names(
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
    nonletters=1,  # need min. 1 non-letter characters (digits, specials, anything)
)


def validate_password(value):
    errors = policy.test(value)
    if errors:
        raise ValidationError('Not a valid password')


class BaseUserSchema(Schema):
    email = fields.Email(required=True)
    # full_name = fields.String(required=True, validate=validate.Length(min=3, max=256))
    full_name = fields.String(required=True, validate=validate.And(validate.Length(min=3, max=50), validate_name))

    # @validates('full_name')
    # def validate_name(self, name):
    #     if len(name) < 3 or len(name) > 256:
    #         raise ValidationError('Length must be between 3 and 256 characters')
    #     try:
    #         first_name, last_name = name.split()
    #     except ValueError as e:
    #         raise ValidationError('Invalid name! Expected two names')


class UserSignInSchema(BaseUserSchema):
    password = fields.String(required=True,
                             validate=validate.And(validate.Length(min=8, max=256), validate_password))


class SingleClothSchemaBase(Schema):
    name = fields.String(required=True)
    color = fields.Enum(ColorEnum, by_value=True, required=True)
    size = fields.Enum(SizeEnum, by_value=True, required=True)
    photo = fields.String(required=True)


class SingleClothSchemaIn(SingleClothSchemaBase):
    pass


class UserOutSchema(BaseUserSchema):
    id = fields.Integer()
    clothes = fields.List(fields.Nested(SingleClothSchemaBase), many=True)


class SingleClothSchemaOut(SingleClothSchemaBase):
    id = fields.Integer()
    create_on = fields.DateTime()
    updated_on = fields.DateTime()


class UserRegisterResource(Resource):
    @validate_schemas(UserSignInSchema)
    def post(self):
        data = request.get_json()
        data['password'] = generate_password_hash(data['password'], 'SHA256')
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return {"token": user.encode_token()}
        # return UserOutSchema().dump(user), {"token": user.encode_token()}

    def get(self, pk):
        user = User.query.filter_by(id=pk).first()  # .all()
        return UserOutSchema().dump(user)


class ClothesResource(Resource):
    @auth.login_required
    @permission_required([UserRoles.admin, UserRoles.user])
    @validate_schemas(SingleClothSchemaIn)
    def post(self):
        data = request.get_json()
        clothes = Clothes(**data)
        db.session.add(clothes)
        db.session.commit()
        return SingleClothSchemaOut().dump(clothes)


api.add_resource(UserRegisterResource, '/register')
api.add_resource(ClothesResource, '/clothes')

if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)
