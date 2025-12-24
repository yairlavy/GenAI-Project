from pydantic import BaseModel
from typing import Optional


# Sub-models
class DateModel(BaseModel):
    day: str = ""
    month: str = ""
    year: str = ""


class AddressModel(BaseModel):
    street: str = ""
    houseNumber: str = ""
    entrance: str = ""
    apartment: str = ""
    city: str = ""
    postalCode: str = ""
    poBox: str = ""


class MedicalInstitutionFieldsModel(BaseModel):
    healthFundMember: str = ""
    natureOfAccident: str = ""
    medicalDiagnoses: str = ""


# Full Injury Form Model
class InjuryFormModel(BaseModel):
    lastName: str = ""
    firstName: str = ""
    idNumber: str = ""
    gender: str = ""

    dateOfBirth: DateModel = DateModel()
    address: AddressModel = AddressModel()

    landlinePhone: str = ""
    mobilePhone: str = ""
    jobType: str = ""

    dateOfInjury: DateModel = DateModel()
    timeOfInjury: str = ""

    accidentLocation: str = ""
    accidentAddress: str = ""
    accidentDescription: str = ""
    injuredBodyPart: str = ""

    signature: str = ""

    formFillingDate: DateModel = DateModel()
    formReceiptDateAtClinic: DateModel = DateModel()

    medicalInstitutionFields: MedicalInstitutionFieldsModel = MedicalInstitutionFieldsModel()

# check the model
if __name__ == "__main__":
    form = InjuryFormModel()
    print(form.model_dump())
