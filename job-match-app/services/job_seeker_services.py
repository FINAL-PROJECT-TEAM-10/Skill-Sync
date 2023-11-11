from data.database import read_query, insert_query, update_query
from fastapi import Response
from fastapi.responses import JSONResponse
from common.job_seeker_status_check import recognize_status, convert_status
from app_models.job_seeker_models import JobSeekerInfo, JobSeekerOptionalInfo
from app_models.job_seeker_models import JobSeeker
from services.authorization_services import get_password_hash
from services import admin_services

def read_seekers():

    data = read_query('SELECT * FROM job_seekers')
    return data

def contacts_info_for_seeker(contact_id: int):

    data = read_query('SELECT email, address, telephone, locations_id FROM employee_contacts WHERE id = ?', (contact_id,))


    return data

def location_id_from_contacts(contact_id: int):

    data = read_query('SELECT locations_id FROM employee_contacts WHERE id = ?', (contact_id,))

    return data[0][0]

def location_finder(location_id: int):

    data = read_query('SELECT city, country FROM locations WHERE id = ?', (location_id,))

    if data:
        return data
    else:
        return None

def job_seeker_info_username(username: str):

    job_seeker = read_query('SELECT summary, employee_contacts_id, busy FROM job_seekers WHERE username = ?', (username,))
    status = recognize_status(job_seeker[0][2])
    location_id_contacts = location_id_from_contacts(job_seeker[0][1])
    location_seeker = location_finder(location_id_contacts)
    summary = job_seeker[0][0]
    location = location_seeker[0][0]

    return JobSeekerInfo(summary=summary, location=location, status=status)

def check_seeker_exists(username: str):

    check = read_query('SELECT * FROM job_seekers WHERE username = ?', (username,))

    return bool(check)


def edit_info(username: str, summary: str, city: str, status: str):

    converted_status = convert_status(status)
    update_query('UPDATE job_seekers SET summary = ?, busy = ? WHERE username = ?', (summary, converted_status, username))

    return JSONResponse(status_code=200, content='You successfully edited your personal info')

def get_job_seeker_info(username: str):

    data = read_query('SELECT * FROM job_seekers WHERE username = ?', (username,))

    return data


# TODO: Consider having a more encompassing get function
def get_seeker(username) -> None | JobSeeker:
    seeker_data = read_query('''
        SELECT js.id, js.username, ec.email, js.first_name, js.last_name, js.summary, js.blocked
        FROM job_seekers as js, employee_contacts as ec
        WHERE js.employee_contacts_id = ec.id AND js.username = ?
        ''', (username,))

    return next((JobSeeker.from_query_results(*row) for row in seeker_data), None)


def create_seeker(username, password, first_name, last_name, email, city, country):


    location_id = admin_services.find_location_id(city, country)

    if not location_id:
        location_id = admin_services.create_location(city, country)

    password = get_password_hash(password)
    adress = ' '
    telephone = ' '
    busy = False
    blocked = False
    approved = 0

    new_contact = insert_query('''
    INSERT INTO employee_contacts
    (email, address, telephone,locations_id)
    VALUES (?,?,?,?)
''', (email, adress, telephone, location_id)
    )

    new_seeker = insert_query('''
    INSERT INTO job_seekers
    (username, password, first_name, last_name, busy, blocked, approved, employee_contacts_id)
    VALUES (?,?,?,?,?,?,?,?)
    ''', (username, password, first_name, last_name, busy, blocked, approved, new_contact)
                              )
    
    return JSONResponse(status_code=200, content='Seeker was created')