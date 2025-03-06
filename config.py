import tomllib


class Config:
    _instance = None

    def __new__(cls, file_path='env.toml'):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config(file_path)
        return cls._instance

    def _load_config(self, file_path):
        with open(file_path, 'rb') as file:
            self.config = tomllib.load(file)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if type(value) is dict:
                value = value.get(k, {})
            elif type(value) is list:
                value = value[int(k)]
            else:
                break
        return value if value else default


wilayas_dict = {
    "adrar": 1,
    "chlef": 2,
    "laghouat": 3,
    "oum el bouaghi": 4,
    "batna": 5,
    "bejaia": 6,
    "biskra": 7,
    "bechar": 8,
    "blida": 9,
    "bouira": 10,
    "tamanrasset": 11,
    "tebessa": 12,
    "tlemcen": 13,
    "tiaret": 14,
    "tizi ouzou": 15,
    "alger": 16,
    "djelfa": 17,
    "jijel": 18,
    "setif": 19,
    "saida": 20,
    "skikda": 21,
    "sidi bel abbes": 22,
    "annaba": 23,
    "guelma": 24,
    "constantine": 25,
    "medea": 26,
    "mostaganem": 27,
    "m'sila": 28,
    "mascara": 29,
    "ouargla": 30,
    "oran": 31,
    "el bayadh": 32,
    "illizi": 33,
    "bordj bou arreridj": 34,
    "boumerdes": 35,
    "el tarf": 36,
    "tindouf": 37,
    "tissemsilt": 38,
    "el oued": 39,
    "khenchela": 40,
    "khenchla": 40,
    "souk ahrass": 41,
    "tipaza": 42,
    "mila": 43,
    "ain defla": 44,
    "naama": 45,
    "ain temouchent": 46,
    "ain timouchent": 46,
    "ghardaia": 47,
    "relizane": 48,
    "m'ghair": 49,
    "m'ghaier": 49,
    "el menia": 50,
    "el meniaa": 50,
    "ouled djellal": 51,
    "bordj baji mokhtar": 52,
    "beni abbes": 53,
    "timimoun": 54,
    "touggourt": 55,
    "djanet": 56,
    "In salah": 57,
    "In guezzam": 58
}


type_dict = {
    "Appels d'offres": [2],
    "Consultations": [1],
    "Avis d'Attribution": [3],
    "Avis d'annulation": [4],
    "Avis d'Infructuosité": [4],
    "Mises en Demeure": [7],
    "Enchères et Adjudications": [5, 6],
    "Opportunités d'affaires": [9],
    "Résiliations": [8],
    "Prorogations": [2],
    "Informations": [0]
}

business_lines_dict = {
    "Aéronautique": 1,
    "Agriculture, Élevage, Forêts et Pêche": 2,
    "Agro Alimentaire": 3,
    "Ameublement et Mobilier": 4,
    "Architecture et Urbanisme": 5,
    "Assurance et Banque": 6,
    "Batiment et Génie Civil": 7,
    "Chimie et Pétrochimie": 8,
    "Equipements Industriels, Outillage et Pièces Détachées": 9,
    "Restauration, Hôtellerie, Équipements pour les Collectivités et Villes": 10,
    "Etudes et Consulting": 11,
    "Études et Consulting": 11,
    "Hydraulique et environnement": 12,
    "Immobilier": 13,
    "Impression, Édition et Communication": 14,
    "Industrie de la Cellulose, Papier, Carton et Emballage": 15,
    "Industries Électriques et Électrotechniques": 16,
    "Industries Manufacturières": 17,
    "Industries Sidérurgiques, Métallurgiques et Mécaniques": 18,
    "Informatique et Bureautique": 19,
    "Médical et Paramédical": 20,
    "Mines, Cimenterie, Agrégats et Granulats": 21,
    "Pharmacie et Parapharmacie": 22,
    "Port, Aéroport et Transit": 23,
    "Sécurité et HSE": 24,
    "Services": 25,
    "Sport et Loisirs": 26,
    "Equipements Scientifiques et Laboratoires": 27,
    "Télécommunication": 28,
    "Transports": 29,
    "Travaux Publics": 30,
    "Industries Électroniques et Matériel Audio-visuel": 31,
    "Autres": 32
}

dataframe_cols = {
    'id': int,
    'title': str,
    'number': str,
    'description': str,
    'contact': str,
    'terms': str,
    'owner': str,
    'due_amount': float,
    'announcement_types': None,
    'business_lines': None,
    'wilaya': str,
    'publish_date': 'datetime64[ns]',
    'due_date': 'datetime64[ns]',
    'status': bool,
}
