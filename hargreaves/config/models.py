class ApiConfiguration:
    _username: str
    _password: str
    _date_of_birth: str
    _secure_number: str

    def __init__(self, username: str, password: str, date_of_birth: str, secure_number: str):
        """
        :param str username: The username to use
        :param str password: The password to use
        :param str date_of_birth: The date of birth in DDMMYY format
        :param str secure_number: Your secure number
        """
        self._username = username
        self._password = password
        self._date_of_birth = date_of_birth
        self._secure_number = secure_number

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def date_of_birth(self):
        return self._date_of_birth

    @property
    def secure_number(self):
        return self._secure_number
