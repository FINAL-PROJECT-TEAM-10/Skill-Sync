from fastapi import APIRouter, Query,Depends, Form, HTTPException
from services import job_ads_services
from fastapi.responses import JSONResponse
from common.auth import get_current_user
from services import job_seeker_services, job_ads_services
from common.separators_validators import parse_skills

job_ads_router = APIRouter(prefix='/job_ads')


@job_ads_router.post('/', description= 'You can create your company job ads from this section.', 
                     tags= {'Job Ads Section'})

def create_new_job_ad(description: str = Form(), location: str = Form(None), remote_location: str = Form(enum=['Yes',"No"]),
                       min_salary: int = Form(), max_salary: int = Form(), 
                      requirements: str = Form(description='Example: python;3,java;2,javascript;1 [1 - Beginner, 2 - Intermidiate, 3 - Advanced]'),
                      current_user_payload=Depends(get_current_user)):
    
    if current_user_payload['group'] != 'companies':
        raise HTTPException(status_code=403,
                            detail ='This option is only available for Companies')
    
    if max_salary and min_salary:
        if max_salary < min_salary:
            raise HTTPException(status_code=400, detail ='The minimum salary cannot be bigger than the maximum salary')
        
    status = 'active'
    requirements_list = parse_skills(requirements)
    
    try:
        requirements_names = [skill.split(';')[0] for skill in requirements_list]
        requirements_levels = [skill.split(';')[1] for skill in requirements_list]
    except IndexError:
        raise HTTPException(status_code=404, detail='Invalid input look at the description')

    if len(requirements_list) < 2:
        raise HTTPException(status_code=400, detail ='You need atleast 2 requirements!')
    if len(requirements_list) > 5:
        raise HTTPException(status_code=400, detail ='The maximum requirements limit of 5 has been reached!')

    company_username = current_user_payload.get('username')
    company_id = job_ads_services.find_company(company_username)

    create_job = job_ads_services.create_job_add(description,location, remote_location, min_salary, max_salary, status, 
                                                 company_id[0][0], requirements_names, requirements_levels)
    return create_job


@job_ads_router.get('/companies', description= 'You can view a specific company job ads from this section.', 
                    tags={'Job Ads Section'})

def view_different_specific_company_job_ads(name_of_company: str = Query(), current_user_payload=Depends(get_current_user)):
    
    if current_user_payload['group'] != 'companies':
        raise HTTPException(status_code=403,
                            detail ='This option is only available for Companies')
    
    if not job_ads_services.check_company_exist(name_of_company):
        raise HTTPException(status_code=404, detail ='This company name doesnt exist')
    view_ads = job_ads_services.view_all_job_ads(name_of_company)

    result = []

    for data in view_ads:
        data_dict = {
            "Job AD ID": data[0],
            "Description": data[1],
            "Minimum Salary": data[2],
            "Maximum Salary": data[3],
            "Location": job_seeker_services.get_cv_location_name(job_ads_services.get_cv_location_id(data[0])),
            "Status": data[4],
            "Date Posted": data[5]
        }
         
        result.append(data_dict)

    if not result:
        raise HTTPException(status_code=202, detail='There are no current active ads for this Company')

    return result


@job_ads_router.get('/information', description= 'You can view your company active/archived job ads from this section.', 
                    tags= {'Job Ads Section'})

def view_active_or_archived_job_ads(status: str = Query(enum= ['active', 'archived']),current_user_payload=Depends(get_current_user)):
    
    if current_user_payload['group'] != 'companies':
        raise HTTPException(status_code=403,
                            detail ='This option is only available for Companies')
    
    company_ads = current_user_payload.get('username')

    company_id = job_ads_services.find_company(company_ads)
    get_company_ads = job_ads_services.view_job_ads_by_id(company_id[0][0], status)

    return get_company_ads


@job_ads_router.put('/edit/information', description= 'You can edit your job ad from this section.', 
                    tags={'Job Ads Section'})

def edit_your_job_ad(job_ad_id: int = Form(), 
                     description: str = Form(None), 
                     min_salary: int = Form(None), 
                     max_salary: int = Form(None), 
                     requirements: str = Form(None, 
                     description= 'Example: python;3,java;2,javascript;1 [1 - Beginner, 2 - Intermidiate, 3 - Advanced]'), 
                     current_user_payload=Depends(get_current_user)):
    
    if current_user_payload['group'] != 'companies':
        raise HTTPException(status_code=403,
                            detail ='This option is only available for Companies')
    
    company_id = current_user_payload.get('id')

    if not job_ads_services.check_owner_company(job_ad_id,company_id):
        raise HTTPException(status_code=400, detail ='That id is not a valid for your job_ads')
    if max_salary and min_salary:
        if max_salary < min_salary:
            raise HTTPException(status_code=400, detail ='The minimum salary cannot be bigger than the maximum salary')

    try:
        requirements_list = parse_skills(requirements)
        requirements_names = [skill.split(';')[0] for skill in requirements_list]
        requirements_levels = [skill.split(';')[1] for skill in requirements_list]

    except IndexError:
        raise HTTPException(status_code=404, detail ='Invalid input look at the description')
    
    except TypeError:
        getting_requirements = job_ads_services.existing_requirements(job_ad_id)
        requirements_names = []
        requirements_levels = []

        try:
            for requirements_id in getting_requirements[0]:
                requirements_name = job_ads_services.find_requirement_by_id(requirements_id)
                requirements_names.append(requirements_name)
                requirement_level = job_ads_services.find_requirements_level(job_ad_id, requirements_id)
                requirements_levels.append(requirement_level)

        except IndexError:
            requirements_names = []
            requirements_list = []

    company_information = job_ads_services.check_company_information(job_ad_id, company_id)

    if min_salary:
        if min_salary > company_information[0][3]:
            raise HTTPException(status_code= 400, detail ='This salary is not a valid one for your current, minimum salary')

    arg_min_salary = min_salary or company_information[0][2]
    arg_max_salary = max_salary or company_information[0][3]
    arg_description = description or company_information[0][1]

    if not description and not min_salary and not max_salary and not requirements:
        raise HTTPException(status_code=202, detail ="You haven't done any changes to your Job_Ad information")

    return job_ads_services.edit_job_ads(company_id, job_ad_id, arg_min_salary, arg_max_salary, 
                                         arg_description, requirements_names, requirements_levels)


@job_ads_router.get('/search/cv', description= 'You can view every recommended CV from this section. Choose the right status for your search.', 
                        tags= ['Company Job Ads Searching/Matching Section'])

def search_recommended_cv_from_job_seeker(job_ad_id: int = Query(description= 'Type your specific job ad id.'),
                              status: str =  Query(enum= ['Best', 'Very Good', 'Good', 'Bad', 'Worst']),
                              current_user_payload=Depends(get_current_user)):
     
    if current_user_payload['group'] != 'companies':
       return JSONResponse(status_code=403,
                            content='This option is only available for Companies')
     
    getting_owner = current_user_payload.get('id')

    if not job_ads_services.find_a_company_owner_by_id(job_ad_id):
        raise HTTPException(status_code=400, detail= "The job ad you chose is archived or its invalid")

    return job_ads_services.calculate_percantage_cv(job_ad_id, status, threshold_percent = None, 
                                                    perms = "Company")


@job_ads_router.get('/search/cv/salary', description= "You can select different salary range and search for available cv's.", 
                    tags= ['Company Job Ads Searching/Matching Section'])

def search_salary_based_on_different_cvs(job_ad_id: int = Query(), minimum_salary: int = Query(), 
                              maximum_salary: int = Query(), threshold_percent : int = Query(),
                                current_user_payload=Depends(get_current_user)):
     
    if current_user_payload['group'] != 'companies':
       return JSONResponse(status_code=403,
                            content='This option is only available for Companies')

    if maximum_salary and minimum_salary:
       if maximum_salary < minimum_salary:
            return JSONResponse(status_code=400, content='The minimum salary cannot be bigger than the maximum salary')

    getting_owner = current_user_payload.get('id')
    
    if threshold_percent > 100:
        raise HTTPException(status_code=400, detail='The threshold should be lower than 100%')
    
    if not job_ads_services.find_a_company_owner_by_id(job_ad_id):
       raise HTTPException(status_code=400, detail= "The job ad you chose is archived or its invalid")

    percantage_based_on_salary = 'All'
    salary = [minimum_salary,maximum_salary]
    perms = 'Company'

    return job_ads_services.calculate_percantage_cv(job_ad_id, percantage_based_on_salary, 
                                                    perms, threshold_percent, salary)

