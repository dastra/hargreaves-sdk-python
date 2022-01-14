class ApiConfiguration:

    def __init__(self, username: str, password: str, date_of_birth: str, secure_number: str):
        """
        :param str username: The username to use
        :param str password: The password to use
        :param str date_of_birth: The date of birth in DDMMYY format
        :param str secure_number: Your secure number
        """
        self.__username = username
        self.__password = password
        self.__date_of_birth = date_of_birth
        self.__secure_number = secure_number

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def date_of_birth(self):
        return self.__date_of_birth

    @property
    def secure_number(self):
        return self.__secure_number
