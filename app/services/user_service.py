from app import db
from app.models.role import Role
from app.models.user import User
from app.services.base_service import BaseService
from app.mappers.user_mapper import UserMapper
import bcrypt


class UserService(BaseService):
    def find_all(self):
        return [UserMapper.entity_to_dto(user) for user in User.query.filter_by(active=True).all()]

    def find_all_no_dto(self):
        return User.query.all()

    def find_one(self, entity_id: int):
        return UserMapper.entity_to_dto(User.query.filter_by(userid=entity_id).first())

    def find_one_by(self, **kwargs) -> User:
        return User.query.filter_by(**kwargs).first()

    def insert(self, data: User):
        password = data.userpassword.encode('utf-8')
        salt = bcrypt.gensalt()
        data.userpassword = bcrypt.hashpw(password, salt).decode('utf-8')

        try:
            db.session.add(data)
            db.session.commit()
        except:
            db.session.rollback()

        return self.find_one(data.userid)

    def update(self, entity_id: int, data: User):
        user = User.query.filter_by(userid=entity_id).first()
        user.useremail = data.useremail
        user.userdescription = data.userdescription

        role_user = Role.query.filter_by(rolename="USER").one()
        user.add_role(role_user)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            return None

        return UserMapper.entity_to_dto(user)

    def delete(self, entity_id: int):
        user = User.query.filter_by(userid=entity_id).first()

        if user is not None:
            db.session.delete(user)
            db.session.commit()

        return user.userid

    def login(self, user: User):
        to_login = self.find_one_by(username=user.username)

        if to_login is not None and bcrypt.checkpw(user.userpassword.encode('utf-8'), to_login.userpassword.encode('utf-8')):
            return to_login

        return None