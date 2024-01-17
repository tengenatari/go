

class UserLogin():
    def create_from_db(self, User):
        self.__user = User
        return self


    def create(self, user):
        self.__user = user
        return self


    def is_authenticated(self):
        return True


    def is_active(self):
        return True


    def is_anonymous(self):
        return False


    def get_id(self):
        return str(self.__user.id)

