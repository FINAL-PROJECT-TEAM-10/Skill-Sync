from fastapi import APIRouter, Query, Body,Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from services import company_services
from services import job_ads_services
from app_models.company_models import Company
from typing import Annotated
from common.auth import get_current_user

companies_router = APIRouter(prefix='/companies',tags={'Everything available for Companies'})

@companies_router.get('/', description= 'You can view every company from here')
def view_all_companies(current_user_payload=Depends(get_current_user)):
    if current_user_payload['group'] != 'companies':
        return JSONResponse(status_code=403,
                            content='This option is only available for Companies')
    
    get_companies = company_services.read_companies()
    result = []

    for data in get_companies:
        get_companies_info = company_services.read_company_adress(data[0])
        get_companies_location = company_services.read_company_location(get_companies_info[0][4])
        data_dict = {
            "Company Name": data[1],
            "Email": get_companies_info[0][1],
            "Work Adress": get_companies_info[0][2],
            "Telephone": get_companies_info[0][3],
            "City": get_companies_location[0][0],
            "Country": get_companies_location[0][1]
        }
         
        result.append(data_dict)

    return result

@companies_router.post('/register', response_model=Company)
def company_registration(Company_Name: str = Query(), Password: str = Query(), 
                         Company_City: str = Query(), Company_Country: str = Query(), Company_Adress: str = Query(),
                         Telephone_Number: int = Query(),Email_Adress: str = Query(),):
    

    if company_services.check_company_exist(Company_Name):
        return JSONResponse(status_code=409,content=f'Company with this {Company_Name} already exists.')

    create_company = company_services.create_company(Company_Name, Password, Company_City, Company_Country, 
                                                     Company_Adress, Telephone_Number, Email_Adress)
    
    return create_company


@companies_router.get('/information')
def your_company_information(current_user_payload=Depends(get_current_user)):
    
    if current_user_payload['group'] != 'companies':
            return JSONResponse(status_code=403,
                                content='This option is only available for Companies')  
    
    company_name = current_user_payload.get('username')

    all_information = []
    
    get_company_information = company_services.get_company_info_name(company_name)
    get_location_id = company_services.location_id(company_name[0][1])
    company_location_from_id = company_services.find_location(get_location_id)
    company_dict = {
         "Company Name": get_company_information[0][0],
         "Company Description": get_company_information[0][1],
         "Company City": company_location_from_id[0][0]

    }

    all_information.append(company_dict)

    return all_information