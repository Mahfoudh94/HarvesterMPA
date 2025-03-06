from sqlalchemy.orm import Session

from database import base_engine
from models import BusinessLine, AnnouncementType

business_lines = {
    'Aeronautics': 1,
    'Agriculture_Breeding_Forestry_and_Fishing': 2,
    'Agri_Food_Industry': 3,
    'Furniture': 4,
    'Architecture_and_Urban_Planning': 5,
    'Insurance_and_Bank': 6,
    'Building_Materials': 33,
    'Building_And_Civil_Engineering': 7,
    'Chemistry_Petrochemistry_Energy_and_Petroleum_Services': 8,
    'Industrial_Equipment_Tools_and_Spare_Parts': 9,
    'Catering_Hotel_Business_Equipment_for_Local_Authorities_and_Cities': 10,
    'Studies_Consulting_Training_and_Certification': 11,
    'Hydraulics_and_Environment': 12,
    'Real_Estate_Business': 13,
    'Printing_Publishing_and_Communication': 14,
    'Cellulose_Industry_Paper_Cardboard_and_Packaging': 15,
    'Electrical_and_Electrotechnical_Industries': 16,
    'Manufacturing_Industries': 17,
    'Steel_Metallurgy_and_Mechanical_Industries': 18,
    'Computer_Science_and_Office_Automation': 19,
    'Medical_and_Paramedical_Business': 20,
    'Mine_Cement_Industry_Aggregate_and_Granular': 21,
    'Pharmacy': 22,
    'Harbours_and_Airports': 23,
    'Security': 24,
    'Services': 25,
    'Sports_and_Recreation': 26,
    'Scientific_Equipment_and_Laboratories': 27,
    'Telecommunications': 28,
    'Transportation': 29,
    'Public_Works': 30,
    'Electronic_Industries_and_Audio_Visual_Equipment': 31,
    'Others': 32,
}

announcement_types = {
    'Consultations': 1,
    'CallsForTenders': 2,
    'Awards': 3,
    'Cancellations': 4,
    'Unsuccessful': 5,
    'AuctionSales': 6,
    'Adjudications': 7,
    'FormalNotices': 8,
    'Terminations': 9,
    'Prorogations': 10,
    'National': 12,
    'International': 14,
}

session = Session(base_engine)

def seed_business_lines():
    for business_line, id in business_lines.items():
        session.add(
            BusinessLine(id=id, name=business_line.replace('_', ' '))
        )

def seed_types():
    for business_line, id in announcement_types.items():
        session.add(
            AnnouncementType(id=id, name=business_line.replace('_', ' '))
        )