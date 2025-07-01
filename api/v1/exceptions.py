from rest_framework.exceptions import APIException
from rest_framework import status


class BaseAPIException(APIException):
    default_detail = "An error occurred during API operation."
    default_code = "api_error"


class CategoryNotFound(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Category not found."
    default_code = "category_not_found"


class InvalidCategoryData(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid category data."
    default_code = "invalid_category_data"
