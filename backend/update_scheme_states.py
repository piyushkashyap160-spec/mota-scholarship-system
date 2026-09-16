import json
from app.database import SessionLocal
from app.models import Scheme

ALL_INDIAN_STATES_AND_UTS = [
    "Andaman and Nicobar Islands",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chandigarh",
    "Chhattisgarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi (NCT)",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu and Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Ladakh",
    "Lakshadweep",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Puducherry",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
]

db = SessionLocal()
schemes = db.query(Scheme).all()
for s in schemes:
    fields = list(s.form_fields or [])
    modified = False
    for f in fields:
        if f.get("id") == "state":
            f["options"] = ALL_INDIAN_STATES_AND_UTS
            modified = True
    if modified:
        s.form_fields = fields
        print(f"Updated states list for scheme {s.code} to all 36 States and UTs.")

db.commit()
db.close()
print("Migration completed successfully!")
