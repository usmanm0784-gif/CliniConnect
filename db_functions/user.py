from core.db import get_db_connection   

# Connect to database
db = get_db_connection()
users_collection = db["users"]  
patients_collection = db["patients"]  
doctors_collection = db["doctors"]


async def get_user_by_email(email: str):

    existing_user = await users_collection.find_one({"email": email})

    return existing_user


async def create_user_as_doctor(email, password):

    existing_user = await get_user_by_email(email)

    if existing_user:

        await users_collection.update_one(
            {
                "_id": existing_user["_id"]
            },
            {
                "$set": {
                    "doctor_password": password
                }
            }
        )
        return existing_user["_id"]


    else:

        result = await users_collection.insert_one({
            "email": email,
            "doctor_password": password
        })
        print(result.inserted_id)
        return result.inserted_id
    
async def create_user_as_patient(email, password):

    existing_user = await get_user_by_email(email)

    if existing_user:

        await users_collection.update_one(
            {"_id": existing_user["_id"]},
            {
                "$set":{
                    "patient_password": password
                }
            }
        )

        return existing_user

    else:

        result = await users_collection.insert_one({
            "email": email,
            "patient_password": password
        })

        return result

async def create_doctor(user_id, credentials):
    doctor_result = await doctors_collection.insert_one({
        "_id": user_id,
        "title": credentials.title,
        "name": credentials.name,
        "phone_number": credentials.phone_number,
        "city": credentials.city,
        "specialization": credentials.specialization
    })
    return doctor_result


async def create_patient(user_id, credentials):
    patient_result = await patients_collection.insert_one({
        "_id": user_id,
        "name": credentials.name,
        "phone_number": credentials.phone_number
    })

    return patient_result
    
async def get_user_by_email_and_role(email, role):
    user =  await users_collection.find_one({"email": email,"role": role})
    return user

async def get_user_by_id(id):
    user = await users_collection.find_one({"_id": id})
    return user


async def add_doctor_password(user_id, password):

    await users_collection.update_one(
        {
            "_id": user_id
        },
        {
            "$set": {
                "doctor_password": password
            }
        }
    )

async def add_patient_password(user_id, password):

    await users_collection.update_one(
        {
            "_id": user_id
        },
        {
            "$set": {
                "patient_password": password
            }
        }
    )