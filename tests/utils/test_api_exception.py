from src.utils import APIException
import pytest


def test_api_exception():
    exc = APIException("error")
    
    assert str(exc) == "error"
    assert exc.status_code == 400
    assert isinstance(exc, Exception)

def test_api_exception_with_diferent_code():
    exc = APIException("error", 300)

    assert str(exc) == "error"
    assert exc.status_code == 300
    assert isinstance(exc, Exception)

def test_raise_exception():
    with pytest.raises(APIException) as e:
        raise APIException("fail", 500)
    assert e.value.status_code == 500
    assert str(e.value) == "fail"