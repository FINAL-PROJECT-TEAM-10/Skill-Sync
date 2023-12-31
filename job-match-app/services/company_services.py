from data.database import read_query, insert_query, update_query, update_queries_transaction
from fastapi.responses import JSONResponse
from app_models.company_models import Company
from services import admin_services, job_seeker_services
from common.country_validators_helpers import *


def read_companies():
    data = read_query('SELECT * FROM companies')
    return data


def read_company_adress(id: int):
    data = read_query('SELECT * FROM company_contacts WHERE company_id = ?', (id,))
    return data


def read_company_location(location_id: int):
    data = read_query('SELECT city,country FROM locations WHERE id = ?', (location_id,))
    return data


def read_company_information(company: str):
    data = read_query('SELECT * FROM companies WHERE id = ?', (company,))

    return next((Company.from_company_result(*row) for row in data), None)


def get_company(username) -> None | Company:
    company_data = read_query('''
        SELECT c.id, c.username, cc.email, cc.address, cc.telephone, l.country, l.city, c.blocked
        FROM companies as c, company_contacts as cc, locations as l
        WHERE c.username = ? AND cc.company_id = c.id AND cc.locations_id = l.id
        ''', (username,))

    return next((Company.from_query_result(*row) for row in company_data), None)


def get_company_by_email(email):
    company_data = read_query('''
        SELECT c.id, c.username, cc.email, cc.address, cc.telephone, l.country, l.city, c.blocked
        FROM companies as c, company_contacts as cc, locations as l
        WHERE cc.email = ? AND cc.company_id = c.id AND cc.locations_id = l.id
        ''', (email,))

    return next((Company.from_query_result(*row) for row in company_data), None)


def check_company_exist(name: str):
    data = read_query('SELECT username FROM companies WHERE username = ?', (name,))
    return bool(data)


def company_exists_by_id(id: int) -> bool:
    return any(read_query('''SELECT id from companies WHERE id = ?''',
                          (id,)))


def find_company_id_byusername(nickname: str):
    data = read_query('SELECT id FROM companies WHERE username = ?', (nickname,))
    return data[0][0]


def create_company(Company_Name, Password, Company_City, Company_Country, 
                   Company_Adress, Telephone_Number, Email_Adress):
    
    from services.authorization_services import get_password_hash
    location_id = admin_services.find_location_id(Company_City, Company_Country)

    if not location_id:
        location_id = admin_services.create_location(Company_City, Company_Country)

    password = get_password_hash(Password)

    create_new_company = insert_query('''
        INSERT INTO companies
        (username,password)
        VALUES (?,?)
        ''', (Company_Name, password,))

    company_id = find_company_id_byusername(Company_Name)

    create_new_company_contact = insert_query('''
    INSERT INTO company_contacts
    (email, address, telephone, locations_id,company_id)
    VALUES (?,?,?,?,?)
    ''', (Email_Adress, Company_Adress, Telephone_Number, location_id, company_id,))

    raise HTTPException(status_code=200, detail='Your company has been created')


def location_id(contact_id: int):
    data = read_query('SELECT locations_id FROM company_contacts WHERE company_id = ?', (contact_id,))

    return data[0][0]


def find_location(location_id: int):
    data = read_query('SELECT city, country FROM locations WHERE id = ?', (location_id,))

    if data:
        return data
    else:
        return None


def get_company_info_name(company_name: str):
    company = read_query('SELECT username,description FROM companies WHERE username = ?', (company_name,))

    return company


def everything_from_companies_by_username(username: str):
    company = read_query('SELECT * FROM companies WHERE username = ?', (username,))

    return company


def edit_company_information(username: str, description: str, city: str, address: str, telephone: int):
    company_id = find_company_id_byusername(username)

    update_query('UPDATE companies SET description = ? WHERE username = ?', (description, username,))
    update_query('UPDATE company_contacts SET address = ?, telephone = ? WHERE company_id = ?',
                 (address, telephone, company_id,))

    if not job_seeker_services.find_location_by_city(city):

        country = find_country_by_city(city)
        insert_query('INSERT INTO locations(city,country) VALUES (?,?)',(city,country,))
        location_id = job_seeker_services.find_location_id_by_city_country(city,country)
        update_query('UPDATE company_contacts SET locations_id = ? WHERE company_id = ?',(location_id,company_id,))

    else:
        
        location_id = job_seeker_services.find_location_id_by_city(city)
        update_query('UPDATE company_contacts SET locations_id = ? WHERE company_id = ?', (location_id, company_id,))

    raise HTTPException(status_code=200, detail="You successfully edited your personal company information")


def find_company_id_byusername_for_job_seeker(id: int):
    data = read_query('SELECT username FROM companies WHERE id = ?', (id,))
    return data[0][0]


def view_all_cvs():
    data = read_query('SELECT * FROM mini_cvs WHERE status = "Active" AND main_cv = 1')

    if data:
        ads = [{'CV Creator': job_seeker_services.get_username_by_id(row[6]), 'Cv Description': row[3], 'Minimum Salary': row[1], 
                'Maximum Salary': row[2], 'Location': job_seeker_services.get_cv_location_name(job_seeker_services.get_cv_location_id(data[0])), 
                'Status': row[4], 'Date Posted': row[5]} for row in data]
        return ads
    
    else:
        raise HTTPException(status_code=404, detail='No cvs found!')

def find_matched_job_ads(company_id: int):

    data = read_query('SELECT * FROM job_ads WHERE companies_id = ? AND status = "archived"',(company_id,))

    return len(data)


def find_company_email_username_by_job_ad(job_ad_id):
    data = read_query('''
        SELECT email, username
        FROM companies as c
        JOIN company_contacts as cc ON c.id = cc.company_id
        JOIN job_ads as ja ON ja.companies_id = c.id
        WHERE ja.id = ?
        ''', (job_ad_id,)
    )

    return next((row for row in data), None)
