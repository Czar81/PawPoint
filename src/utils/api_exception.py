class APIException(Exception):
    """
    Verify that a payment method belongs to a user.

    :param conn: Active database connection
    :param id_payment: Payment ID
    :param id_user: User ID
    :return: True if the payment belongs to the user, False otherwise
    """

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code
