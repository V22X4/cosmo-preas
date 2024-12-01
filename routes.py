from fastapi import FastAPI, HTTPException, Query, Path, Body, Response
from typing import List, Optional, Dict, Any
from database import get_async_database
from models import Student
from bson import ObjectId

app = FastAPI(
    title="Student Management System",
    description="API for managing student records",
    version="1.0.0"
)

@app.post("/students", status_code=201, responses={
    201: {
        "description": "A JSON response sending back the ID of the newly created student record.",
        "content": {
            "application/json": {
                "example": {
                    "id": "string"
                }
            }
        }
    }
})
async def create_student(
    student_data: Dict[str, Any] = Body(
        example={
            "name": "string",
            "age": 0,
            "address": {
                "city": "string",
                "country": "string"
            }
        }
    )
):
    """
    API to create a student in the system. All fields are mandatory and required while creating the student in the system.
    """
    try:
        student = Student(
            name=student_data['name'], 
            age=student_data['age'], 
            address=student_data['address']
        )
        
        db = await get_async_database()
        result = await db.students.insert_one(student.to_dict())
        return {"id": str(result.inserted_id)}
    
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/students", responses={
    200: {
        "description": "A list of students matching the query filters.",
        "content": {
            "application/json": {
                "example": {
                    "data": [
                        {"name": "string", "age": 0},
                        {"name": "string", "age": 0}
                    ]
                }
            }
        }
    }
})
async def list_students(
    country: Optional[str] = Query(
        None, 
        description="To apply filter of country. If not given or empty, this filter should be applied.",
    ),
    age: Optional[int] = Query(
        None, 
        description="Only records which have age greater than or equal to the provided age should be present in the result. If not given or empty, this filter should be applied.",
    )
):
    """
    An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below.
    """
    db = await get_async_database()
    query = {}
    
    if country:
        query["address.country"] = country
    if age is not None:
        query["age"] = {"$gte": age}
    
    cursor = db.students.find(query)
    students = await cursor.to_list(length=1000)
    
    return {
        "data": [
            {
                "name": student["name"],
                "age": student["age"]
            } for student in students
        ]
    }

@app.get("/students/{id}", responses={
    200: {
        "description": "A student record returned by ID.",
        "content": {
            "application/json": {
                "example": {
                    "name": "string",
                    "age": 0,
                    "address": {
                        "city": "string",
                        "country": "string"
                    }
                }
            }
        }
    },
    404: {
        "description": "Student not found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Student not found"
                }
            }
        }
    }
})
async def fetch_student(
    id: str = Path(
        ..., 
        description="The ID of the student previously created.",
    )
):
    """
    Fetch a specific student by their ID
    """
    db = await get_async_database()
    student = await db.students.find_one({"_id": ObjectId(id)})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student["id"] = str(student["_id"])
    del student["_id"]
    return student

@app.patch("/students/{id}", status_code=204, responses={
    204: {
        "description": "No content. The student record was successfully updated.",
        "content": {
            "application/json": {
                "example": {}
            }
        }
    },
    404: {
        "description": "Student not found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Student not found"
                }
            }
        }
    }
})
async def update_student(
    id: str = Path(
        ..., 
        description="The ID of the student previously created.",
    ),
    student_update: Dict[str, Any] = Body(
        example={
            "name": "string",
            "age": 0,
            "address": {
                "city": "string",
                "country": "string"
            }
        }
    )
):
    """
    Update an existing student record.
    
    - Partial updates are supported
    - Only provided fields will be updated
    """
    db = await get_async_database()
    
    # Define allowed fields
    ALLOWED_TOP_LEVEL_FIELDS = {'name', 'age', 'address'}
    ALLOWED_ADDRESS_FIELDS = {'city', 'country'}
    
    # Validate input fields
    for key in student_update:
        if key not in ALLOWED_TOP_LEVEL_FIELDS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid field: {key}. Allowed fields are: {', '.join(ALLOWED_TOP_LEVEL_FIELDS)}"
            )
    
    # Validate address fields if address is present
    if 'address' in student_update:
        for key in student_update['address']:
            if key not in ALLOWED_ADDRESS_FIELDS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid address field: {key}. Allowed fields are: {', '.join(ALLOWED_ADDRESS_FIELDS)}"
                )
    
    # Fetch the current student document first
    student = await db.students.find_one({"_id": ObjectId(id)})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Prepare update data with only allowed fields
    update_data = {}
    
    # Handle top-level fields
    if 'name' in student_update:
        update_data['name'] = student_update['name']
    
    if 'age' in student_update:
        update_data['age'] = student_update['age']
    
    # Handle address updates
    if 'address' in student_update:
        update_data['address'] = student.get('address', {}).copy()
        
        if 'city' in student_update['address']:
            update_data['address']['city'] = student_update['address']['city']
        
        if 'country' in student_update['address']:
            update_data['address']['country'] = student_update['address']['country']
    
    # Perform the update
    result = await db.students.update_one(
        {"_id": ObjectId(id)}, 
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return Response(status_code=204)

@app.delete("/students/{id}", status_code=200, responses={
    200: {
        "description": "Student record successfully deleted.",
        "content": {
            "application/json": {
                "example": {}
            }
        }
    },
    404: {
        "description": "Student not found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Student not found"
                }
            }
        }
    }
})
async def delete_student(
    id: str = Path(
        ..., 
        description="The ID of the student previously created.",
        example="string"
    )
):
    """
    Delete a student record by their ID
    """
    db = await get_async_database()
    result = await db.students.delete_one({"_id": ObjectId(id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {}
