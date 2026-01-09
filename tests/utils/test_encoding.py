from src.utils import JWTManager
import pytest

def test_encode_decode():
    data_to_encode = {"message":"this is a secret, must be encoded"}

    jwt_manager = JWTManager()

    encoded = jwt_manager.encode(data_to_encode)
    decoded = jwt_manager.decode(encoded)

    assert decoded == data_to_encode

def test_encoded_str():
    data_to_encode = {"message":"this is a secret, must be encoded"}
    
    jwt_manager = JWTManager()
    encoded = jwt_manager.encode(data_to_encode)

    assert isinstance(encoded, str)
    
def test_encoded_lenght_3():
    data_to_encode = {"message":"this is a secret, must be encoded"}
    
    jwt_manager = JWTManager()
    encoded = jwt_manager.encode(data_to_encode)

    assert len(encoded.split(".")) == 3

def test_encode_invalid_payload():
    jwt_manager = JWTManager()

    with pytest.raises(ValueError):
        jwt_manager.encode("text")  


def test_decode_malformed_token():
    jwt_manager = JWTManager()

    with pytest.raises(Exception):
        jwt_manager.decode("this-is-not-valid-token")