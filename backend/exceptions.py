from fastapi.exceptions import HTTPException


# class EntityNotFound(HTTPException):
#     def __init__(self, entity_name: str, entity_id: int):
#         super().__init__(
#             status_code=404,
#             detail={
#                 "error": "entity_not_found",
#                 "message": f"Unable to find {entity_name} with id={entity_id}",
#             },
#         )

class EntityNotFound(Exception):
    def __init__(self, entity_name: str, entity_id: int):
        self.error = "entity_not_found"
        self.message = f"Unable to find {entity_name} with id={entity_id}"
