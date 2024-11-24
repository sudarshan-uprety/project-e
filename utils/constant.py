"""Constants StatusCodes and Messages"""

# HTTP Status Codes
SUCCESS = 200
SUCCESS_FETCH = 200
SUCCESS_UPDATED = 200
SUCCESS_CREATED = 201
SUCCESS_DELETED = 204
ERROR_BAD_REQUEST = 400
ERROR_UNAUTHORIZED = 401
ERROR_FORBIDDEN = 403
ERROR_NOT_FOUND = 404
ERROR_INTERNAL_SERVER_ERROR = 500
ERROR_FOUND = 302
SERVICE_UNAVAILABLE = 503
UNPROCESSABLE_ENTITY = 422
RESOURCE_EXISTS = 409
# Success constants


# Error constants
ERROR_DOES_NOT_EXIST = "Resource Does Not Exist."
ERROR_SERVER_DOWN = "Server Down"
DATABASE_CONNECTION_ERRORS = [
    "is the server running", "failure in name resolution", "connection refused"
]
DATABASE_NOT_AVAILABLE_FOR_CONNECTION = "Sorry, but the database is either offline or not accepting connections."
