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
        private_key_path = environ.get("PRIVATE_KEY_PATH")
        public_key_path = environ.get("PUBLIC_KEY_PATH")
        if not private_key_path or not public_key_path:
            raise ValueError("PRIVATE_KEY_PATH and PUBLIC_KEY_PATH must be defined in .env")
        
        try:
            with open(str(private_key_path), "r") as f:
                self.private_key = f.read()
            with open(str(public_key_path), "r") as f:
                self.public_key = f.read()
        except Exception as e:
            raise ValueError(f"Could not read key files: {str(e)}")

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
