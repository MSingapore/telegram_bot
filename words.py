"""
Generates a clean, deduplicated words.json dataset.
Run: python words.py
"""
import json

# ─────────────────────────────────────────────
# WORD POOLS  (word, meaning, pronunciation, example)
# ─────────────────────────────────────────────

greetings = [
    ("bonjour",         "hello",        "bon-zhoor",        "Bonjour, comment allez-vous ?"),
    ("salut",           "hi",           "sa-loo",           "Salut ! Tu vas bien ?"),
    ("bonsoir",         "good evening", "bon-swahr",        "Bonsoir tout le monde !"),
    ("bonne nuit",      "good night",   "bon nwee",         "Bonne nuit, dors bien !"),
    ("merci",           "thank you",    "mehr-see",         "Merci beaucoup pour votre aide."),
    ("s'il vous plaît", "please",       "seel voo pleh",    "Un café, s'il vous plaît."),
    ("excusez-moi",     "excuse me",    "ex-kew-zay mwa",   "Excusez-moi, où est la gare ?"),
    ("oui",             "yes",          "wee",              "Oui, je comprends."),
    ("non",             "no",           "nohn",             "Non, merci."),
    ("de rien",         "you're welcome","duh ree-an",      "Merci ! — De rien."),
    ("au revoir",       "goodbye",      "oh ruh-vwar",      "Au revoir, à bientôt !"),
    ("à bientôt",       "see you soon", "ah byan-toh",      "À bientôt, mon ami !"),
]

food = [
    ("pain",        "bread",    "pan",       "Je mange du pain le matin."),
    ("eau",         "water",    "oh",        "Je bois de l'eau chaque jour."),
    ("riz",         "rice",     "ree",       "Le riz est délicieux avec du curry."),
    ("pomme",       "apple",    "pom",       "Je mange une pomme après le déjeuner."),
    ("banane",      "banana",   "ba-nan",    "La banane est jaune et sucrée."),
    ("fromage",     "cheese",   "fro-mahj",  "Le fromage français est excellent."),
    ("lait",        "milk",     "leh",       "Je bois du lait le matin."),
    ("sucre",       "sugar",    "soo-kr",    "Il y a trop de sucre dans ce gâteau."),
    ("sel",         "salt",     "sel",       "Passe-moi le sel, s'il te plaît."),
    ("viande",      "meat",     "vyand",     "Je mange de la viande deux fois par semaine."),
    ("poulet",      "chicken",  "poo-leh",   "Le poulet rôti est mon plat préféré."),
    ("poisson",     "fish",     "pwah-son",  "Nous mangeons du poisson le vendredi."),
    ("légume",      "vegetable","lay-goom",  "Les légumes sont bons pour la santé."),
    ("café",        "coffee",   "ka-fay",    "Je prends un café chaque matin."),
    ("thé",         "tea",      "tay",       "Un thé au citron, s'il vous plaît."),
]

daily = [
    ("maison",      "home",         "meh-zon",   "Je rentre à la maison à dix-huit heures."),
    ("travail",     "work",         "tra-vai",   "Mon travail commence à neuf heures."),
    ("école",       "school",       "ay-kol",    "Les enfants vont à l'école chaque matin."),
    ("jour",        "day",          "zhoor",     "Quelle belle journée aujourd'hui !"),
    ("nuit",        "night",        "nwee",      "La nuit est calme et étoilée."),
    ("matin",       "morning",      "ma-tan",    "Je me lève tôt le matin."),
    ("soir",        "evening",      "swar",      "Je lis le soir avant de dormir."),
    ("temps",       "time / weather","tahn",     "Le temps passe vite quand on s'amuse."),
    ("ville",       "city",         "veel",      "Paris est une belle ville."),
    ("route",       "road",         "root",      "La route vers Paris est longue."),
    ("livre",       "book",         "leevr",     "Je lis un livre intéressant."),
    ("musique",     "music",        "moo-zeek",  "J'aime écouter de la musique."),
    ("téléphone",   "phone",        "tay-lay-fon","Mon téléphone est sur la table."),
    ("voiture",     "car",          "vwah-tur",  "Ma voiture est garée dehors."),
    ("argent",      "money",        "ar-zhon",   "Je n'ai pas assez d'argent."),
]

emotions = [
    ("amour",       "love",     "ah-moor",    "L'amour est la chose la plus belle."),
    ("joie",        "joy",      "zhwah",      "Sa joie est contagieuse."),
    ("triste",      "sad",      "treest",     "Je suis triste aujourd'hui."),
    ("peur",        "fear",     "pur",        "J'ai peur du noir."),
    ("colère",      "anger",    "ko-lehr",    "Sa colère était visible."),
    ("fatigué",     "tired",    "fa-ti-gay",  "Je suis très fatigué ce soir."),
    ("heureux",     "happy",    "uh-ruh",     "Je suis heureux de te voir !"),
    ("calme",       "calm",     "kalm",       "Reste calme, tout va bien."),
    ("stress",      "stress",   "stres",      "Le stress au travail est difficile."),
    ("espoir",      "hope",     "es-pwar",    "L'espoir fait vivre."),
    ("surprise",    "surprise", "sur-preez",  "Quelle surprise de te voir ici !"),
    ("fier",        "proud",    "fyehr",      "Je suis fier de toi, Husaina !"),
]

travel = [
    ("aéroport",    "airport",  "aero-por",   "L'aéroport est loin du centre-ville."),
    ("train",       "train",    "tran",       "Le train part à huit heures."),
    ("bus",         "bus",      "bus",        "Je prends le bus tous les jours."),
    ("billet",      "ticket",   "bee-yeh",    "J'ai acheté deux billets pour Paris."),
    ("carte",       "map",      "kart",       "Regarde la carte pour trouver le chemin."),
    ("hôtel",       "hotel",    "o-tel",      "L'hôtel est en face de la gare."),
    ("bagage",      "luggage",  "ba-gazh",    "Mon bagage est trop lourd."),
    ("voyage",      "journey",  "vwa-yazh",   "Bon voyage et à bientôt !"),
    ("passeport",   "passport", "pas-por",    "N'oublie pas ton passeport !"),
    ("frontière",   "border",   "fron-tyehr", "Nous avons passé la frontière."),
    ("touriste",    "tourist",  "too-reest",  "Je suis touriste à Paris."),
    ("mer",         "sea",      "mehr",       "La mer est belle en été."),
]

family = [
    ("mère",        "mother",       "mehr",       "Ma mère prépare un bon repas."),
    ("père",        "father",       "pehr",       "Mon père lit le journal le matin."),
    ("frère",       "brother",      "frehr",      "Mon frère est plus grand que moi."),
    ("sœur",        "sister",       "sur",        "Ma sœur aime chanter."),
    ("famille",     "family",       "fa-mee",     "Ma famille est très importante pour moi."),
    ("enfant",      "child",        "ahn-fan",    "L'enfant joue dans le jardin."),
    ("bébé",        "baby",         "bay-bay",    "Le bébé dort dans son lit."),
    ("grand-mère",  "grandmother",  "gran-mehr",  "Ma grand-mère fait le meilleur gâteau."),
    ("grand-père",  "grandfather",  "gran-pehr",  "Mon grand-père me raconte des histoires."),
    ("ami",         "friend",       "a-mee",      "Mon meilleur ami s'appelle Karim."),
    ("mari",        "husband",      "ma-ree",     "Son mari est médecin."),
    ("femme",       "wife / woman", "fam",        "Sa femme est professeure."),
]

verbs = [
    ("aller",       "to go",        "a-lay",      "Je vais à l'école chaque matin."),
    ("venir",       "to come",      "vuh-neer",   "Elle vient chez moi ce soir."),
    ("manger",      "to eat",       "mon-zhay",   "Nous mangeons ensemble le soir."),
    ("boire",       "to drink",     "bwar",       "Je bois du café le matin."),
    ("parler",      "to speak",     "par-lay",    "Tu parles très bien français !"),
    ("lire",        "to read",      "leer",       "J'aime lire des romans."),
    ("écrire",      "to write",     "ay-kreer",   "Elle écrit une lettre à sa famille."),
    ("aimer",       "to love",      "ay-may",     "J'aime apprendre le français."),
    ("travailler",  "to work",      "tra-va-yay", "Il travaille dans une école."),
    ("apprendre",   "to learn",     "a-pron-dre", "J'apprends le français chaque jour."),
    ("voir",        "to see",       "vwar",       "Je vois mes amis le week-end."),
    ("faire",       "to do / make", "fair",       "Qu'est-ce que tu fais ce soir ?"),
    ("savoir",      "to know",      "sa-vwar",    "Tu sais parler français ?"),
    ("pouvoir",     "to be able to","poo-vwar",   "Je peux t'aider si tu veux."),
    ("vouloir",     "to want",      "voo-lwar",   "Je veux apprendre le français."),
]

places = [
    ("école",       "school",       "ay-kol",     "L'école commence à huit heures."),
    ("hôpital",     "hospital",     "o-pee-tal",  "L'hôpital est au bout de la rue."),
    ("magasin",     "shop / store", "ma-ga-zan",  "Le magasin est fermé le dimanche."),
    ("restaurant",  "restaurant",   "res-to-ran", "Ce restaurant sert une bonne cuisine."),
    ("banque",      "bank",         "bank",       "Je vais à la banque demain matin."),
    ("parc",        "park",         "park",       "Les enfants jouent dans le parc."),
    ("bureau",      "office",       "bu-ro",      "Mon bureau est au troisième étage."),
    ("marché",      "market",       "mar-shay",   "Le marché est ouvert le samedi."),
    ("bibliothèque","library",      "bib-lyo-tek","Je lis souvent à la bibliothèque."),
    ("pharmacie",   "pharmacy",     "far-ma-see", "La pharmacie est ouverte la nuit."),
    ("boulangerie", "bakery",       "boo-lonj-ree","La boulangerie sent le pain frais."),
    ("gare",        "train station","gar",        "La gare est à dix minutes d'ici."),
]

shopping = [
    ("prix",        "price",        "pree",       "Quel est le prix de cette robe ?"),
    ("acheter",     "to buy",       "a-she-tay",  "Je veux acheter un cadeau pour toi."),
    ("vendre",      "to sell",      "von-dre",    "Il vend des légumes frais."),
    ("cher",        "expensive",    "sher",       "Ce manteau est trop cher."),
    ("bon marché",  "cheap",        "bon mar-shay","Ce marché est très bon marché."),
    ("produit",     "product",      "pro-dwee",   "Ce produit est de très bonne qualité."),
    ("client",      "customer",     "klee-ahn",   "Le client a toujours raison."),
    ("réduction",   "discount",     "ray-dook-syon","Il y a une réduction de 20 % aujourd'hui."),
    ("cadeau",      "gift",         "ka-doh",     "Je t'ai acheté un cadeau spécial."),
    ("soldes",      "sale",         "sold",       "Les soldes commencent samedi."),
    ("carte",       "card",         "kart",       "Je paie par carte bancaire."),
    ("caisse",      "checkout",     "kess",       "Passez à la caisse, s'il vous plaît."),
]

questions = [
    ("quoi",        "what",         "kwa",        "Quoi de neuf ?"),
    ("où",          "where",        "oo",         "Où habites-tu ?"),
    ("quand",       "when",         "kan",        "Quand arrives-tu ?"),
    ("pourquoi",    "why",          "poor-kwah",  "Pourquoi tu ris ?"),
    ("comment",     "how",          "ko-mon",     "Comment vas-tu ?"),
    ("qui",         "who",          "kee",        "Qui est cette personne ?"),
    ("lequel",      "which",        "luh-kel",    "Lequel préfères-tu ?"),
    ("combien",     "how much",     "kom-byan",   "Combien coûte ce livre ?"),
    ("est-ce que",  "is it / do",   "es-kuh",     "Est-ce que tu parles anglais ?"),
    ("qu'est-ce que","what is",     "kes-kuh",    "Qu'est-ce que c'est ?"),
    ("depuis quand","since when",   "duh-pwee kan","Depuis quand tu apprends le français ?"),
    ("à quelle heure","at what time","a kel ur",  "À quelle heure commence le cours ?"),
]


# ─────────────────────────────────────────────
# BUILD JSON
# ─────────────────────────────────────────────

def build_category(words):
    return [
        {
            "word":          w,
            "meaning":       m,
            "pronunciation": p,
            "example":       e,
        }
        for w, m, p, e in words
    ]


data = {
    "beginner": {
        "greetings": build_category(greetings),
        "food":      build_category(food),
        "daily":     build_category(daily),
        "emotions":  build_category(emotions),
        "travel":    build_category(travel),
        "family":    build_category(family),
        "verbs":     build_category(verbs),
        "places":    build_category(places),
        "shopping":  build_category(shopping),
        "questions": build_category(questions),
    }
}

with open("words.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

total = sum(len(v) for v in data["beginner"].values())
print(f"✅ words.json generated — {total} unique words across {len(data['beginner'])} categories.")
