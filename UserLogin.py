

class UserLogin():

    def create(self, user):
        self.__user = user
        return self

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return str(self.__user.id)

    def get_user(self):
        return self.__user

    def is_admin(self):
        return self.__user.rule.id == 999
