from typing import Dict, Optional, Any
from bson import ObjectId

class Address:
    def __init__(self, city: str, country: str):
        if not city or not country:
            raise ValueError("City and country are required")
        self.city = city
        self.country = country

    def to_dict(self):
        return {
            "city": self.city,
            "country": self.country
        }

class Student:
    def __init__(self, name: str, age: int, address: Dict[str, str]):
        # Validation
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        
        if not isinstance(age, int) or age < 0:
            raise ValueError("Age must be a non-negative integer")
        
        if not isinstance(address, dict):
            raise ValueError("Address must be a dictionary")
        
        self.name = name
        self.age = age
        self.address = Address(
            city=address.get('city'), 
            country=address.get('country')
        )

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "address": self.address.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            name=data['name'],
            age=data['age'],
            address=data['address']
        )