import logging

EXCEPTION_TEXT = "An error occurred when querying device. Details: {error_detail}"


def handle_device_not_handled(exception):
    status_code = 404
    logging.error(EXCEPTION_TEXT.format(error_detail=str(exception)))
    return {
        "detail": str(exception),
        "status": status_code,
        "title": "Not Found",
    }, status_code   

def handle_device_timeout(exception):
    status_code = 504
    logging.error(EXCEPTION_TEXT.format(error_detail=str(exception)))
    return {
        "detail": str(exception),
        "status": status_code,
        "title": "Gateway Timeout",
    }, status_code