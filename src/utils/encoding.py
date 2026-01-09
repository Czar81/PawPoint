from jwt import encode, decode
from os import environ
from dotenv import load_dotenv

load_dotenv()


class JWTManager:
    """
    JSON Web Token (JWT) manager.

    Handles encoding and decoding of JWT tokens using
    asymmetric RSA keys (RS256).
    """

    def __init__(self):
        """
        Encode payload data into a JWT token.

        :param data: Payload data to encode
        :return: Encoded JWT token
        :raises ValueError: If token encoding fails
        """
        self.private_key = environ.get("PRIVATE_KEY")
        self.public_key = environ.get("PUBLIC_KEY")
        if not self.private_key or not self.public_key:
            raise ValueError("PRIVATE_KEY y PUBLIC_KEY must be defiend in .env")

    def encode(self, data):
        """
        Encode payload data into a JWT token.

        :param data: Payload data to encode
        :return: Encoded JWT token
        :raises ValueError: If token encoding fails
        """
        try:
            encoded = encode(data, self.private_key, algorithm="RS256")
            return encoded
        except Exception as e:
            raise ValueError(f"Error encoding JWT: {str(e)}")

    def decode(self, token):
        """
        Encode payload data into a JWT token.

        :param data: Payload data to encode
        :return: Encoded JWT token
        :raises ValueError: If token encoding fails
        """
        try:
            decoded = decode(token, self.public_key, algorithms=["RS256"])
            return decoded
        except Exception as e:
            raise ValueError(f"Error decoding JWT: {str(e)}")
