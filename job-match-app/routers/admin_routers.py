import io
from typing import Annotated
from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from app_models.admin_models import Admin
from app_models.validation_models import ALLOWED_PASSWORD
from common.auth import get_current_user
from common.country_validators_helpers import validate_location
from services import admin_services, upload_services

admin_router = APIRouter(prefix='/admin',tags={'Admins section'})


@admin_router.post('/register', response_model=Admin, responses={
    201: {"description": "Informs of admin creation",
          "content": {"application/json": {"example": {"id": 1,
                                                       "group": "admins",
                                                       "username": "example_admin",
                                                       "email": "admin@example.com"
                                                       }
                                           }
                      }
          },
    403: {"description": "Checks privileges.",
          "content": {
            "text/plain": {
                "example": "Only admins can register other admins."
            }
        }
    },
    409: {
        "description": "Assures admin uniqueness.",
        "content": {
            "text/plain": {"example": "Admin [USERNAME] already exists."}
                   }
        }
}, description= "If you are on our moderation team, you can create a specific admin from this section.")

def add_admin(registration_details: Admin, password: Annotated[ALLOWED_PASSWORD, Body()], current_user_payload=Depends(get_current_user)):
    if current_user_payload['group'] != 'admins':
        raise HTTPException(status_code=403,
                            detail='Only admins can register other admins.')

    if admin_services.admin_exists(registration_details):
        raise HTTPException(status_code=409,
                            detail=f'Admin with username {registration_details.username} already exists.')

    validate_location(registration_details.city, registration_details.country)

    if registration_details.group != 'admins':
        raise HTTPException(status_code=400,
                            detail='This is an endpoint for creating admins only.')
    new_admin = admin_services.create_admin(registration_details, password)
    return JSONResponse(status_code=201,
                        content=new_admin.json())


@admin_router.delete('/temporary_tokens', description='Admins can delete every temporary token from this section. Use with caution!')

def delete_all_temp_tokens(current_user_payload=Depends(get_current_user)):
    if current_user_payload['group'] != 'admins':
        raise HTTPException(status_code=403,
                            detail='Only admins can delete temporary tokens.')

    admin_services.delete_temp_tokens()

    return JSONResponse(status_code=200,
                        content='All temporary tokens were deleted.')


@admin_router.get('/{id}/avatar', description='This section is not for admins only.'
                                              ' It allows other users to view admins avatars.')

def get_admin_avatar(id: int, current_user_payload=Depends(get_current_user)):
    image_data = upload_services.get_picture(id, 'admins')

    if not admin_services.admin_exists_by_id(id):
        raise HTTPException(status_code=404,
                            detail='No such admin.')
    if image_data is None:
        raise HTTPException(status_code=404,
                            detail='No associated picture with the admin.')

    return StreamingResponse(io.BytesIO(image_data), media_type="image/jpeg")

# TODO: Implement mailing history for admins, if implemented, add to readme (low priority)
