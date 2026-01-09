from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .api_exception import APIException
import logging
import traceback

logger = logging.getLogger(__name__)


def register_error_handlers(blueprint):
    """
    Register centralized error handlers for a Flask Blueprint.

    This function attaches multiple exception handlers to the given blueprint
    in order to standardize API error responses and logging behavior.

    Handled exceptions:
        - ValueError
        - IntegrityError (SQLAlchemy)
        - SQLAlchemyError
        - APIException (custom application errors)
        - RecursionError (commonly Redis-related issues)
        - Generic Exception (fallback)

    :param blueprint: Flask Blueprint instance
    """

    @blueprint.errorhandler(ValueError)
    def handle_value_error(e):
        """
        Handle ValueError exceptions.

        Typically raised for invalid input or failed validations.
        Returns HTTP 400 Bad Request.
        """
        logger.warning(f"ValueError: {str(e)}")
        traceback.print_exc()
        return jsonify(error=str(e)), 400

    @blueprint.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        """
        Handle SQLAlchemy IntegrityError exceptions.

        Commonly triggered by constraint violations such as:
        - Unique constraints
        - Foreign key constraints

        Returns HTTP 409 Conflict.
        """
        logger.warning(f"Integrity error: {str(e)}")
        traceback.print_exc()
        return jsonify(error=f"Database integrity error: {e}"), 409

    @blueprint.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        """
        Handle generic SQLAlchemy database errors.

        Used as a fallback for unexpected database-related failures.
        Returns HTTP 500 Internal Server Error.
        """
        logger.error(f"Database error: {str(e)}")
        traceback.print_exc()
        return jsonify(error=f"Internal database error: {e}"), 500

    @blueprint.errorhandler(APIException)
    def handle_api_error(e):
        """
        Handle custom APIException errors.

        APIException allows defining custom error messages and HTTP status codes
        at the business logic layer.
        """
        logger.warning(f"API error: {str(e)}")
        traceback.print_exc()
        return jsonify(error=str(e)), e.status_code

    @blueprint.errorhandler(RecursionError)
    def handle_recursion_error(e):
        """
        Handle RecursionError exceptions.

        This is commonly associated with Redis or caching issues
        such as circular references or excessive recursion depth.
        Returns HTTP 500 Internal Server Error.
        """
        logger.error(f"Recursion error (Redis issue?): {str(e)}")
        traceback.print_exc()
        return jsonify(error="An unexpected error occurred with redis"), 500

    @blueprint.errorhandler(Exception)
    def handle_generic_error(e):
        """
        Handle any unhandled exceptions.

        Acts as a final safety net to prevent server crashes
        and expose a controlled error response.
        Returns HTTP 500 Internal Server Error.
        """
        logger.error(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        return jsonify(error=f"An unexpected error occurred: {e}"), 500
