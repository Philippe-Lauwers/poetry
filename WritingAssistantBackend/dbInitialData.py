# scripts/init_rhyme_schemes.py
import os
import traceback

from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

load_dotenv(os.path.join(os.path.dirname(__file__), '.flaskenv'))
import os
from WritingAssistantBackend.app import create_app
from WritingAssistantBackend.extensions import db
from WritingAssistantBackend.dbModel import (
    Users,
    PoemLanguages,
    RhymeSchemes,
    RhymeSchemeElements,
)

# 1) Build the app and enable SQL echo
app = create_app()

app.config["SQLALCHEMY_ECHO"] = True

language_dict = {"fr": "fr-fr", "en": "en-gb"}

with app.app_context():
    # ---- 1. Create a user ----
    print("-> Creating admin user")
    admin = db.session.query(Users).filter_by(name="admin").first()
    if not admin:
        admin = Users(name="admin")
        db.session.add(admin)
        db.session.commit()
        db.session.expunge(admin)

    # ---- 2. Create PoemLanguages and build the id map ----
    print("-> Creating poem languages")
    poem_language_ids = {}
    for code, iso in language_dict.items():
        pl = PoemLanguages.query.filter_by(language=iso).first()
        if not pl:
            pl = PoemLanguages(language=iso)  # adjust to your actual column names
            db.session.add(pl)
            db.session.flush()
        poem_language_ids[iso] = pl.id
    db.session.commit()
    db.session.expunge(pl)

    # ---- 3. Insert rhyme schemes & elements, rhyme_schemes copied from poembase.py  ----
    rhyme_schemes = {
        "sonnet": ("a", "b", "b", "a", "", "c", "d", "d", "c", "", "e", "f", "e", "", "f", "e", "f"),
        "short": ("a", "b", "a", "b", "", "c", "d", "c", "d"),
        "shorter": ("a", "b", "a", "b"),
        "pantoum": ("a", "b", "c", "d", "", "b", "e", "d", "f", "", "e", "g", "f", "h", "", "g", "a", "h", "c")
        # add the rest...
    }
    print("-> Creating rhyme schemes")
    for scheme_name, elements in rhyme_schemes.items():
        print(f"-> Inserting scheme {scheme_name!r}")
        rs = RhymeSchemes.query.filter_by(rhymeScheme=scheme_name).first()
        if not rs:
            rs = RhymeSchemes(rhymeScheme=scheme_name)
            db.session.add(rs)
            db.session.flush()

        for order, elm in enumerate(elements, start=1):
            for iso, pl_id in poem_language_ids.items():
                rse = db.session.query(RhymeSchemeElements).filter_by(rhymeScheme_id=rs.id, poemLanguage_id=pl_id,
                                                                      order=order).first()
                if not rse:
                    rse = RhymeSchemeElements(
                        rhymeScheme_id=rs.id,
                        poemLanguage_id=pl_id,
                        order=order,
                        rhymeSchemeElement=elm
                    )
                    db.session.add(rse)

    # ---- 4. Commit once ----
    db.session.commit()
    db.session.expunge(rs)
    db.session.expunge(rse)

    import os
    import json
    import pickle
    from WritingAssistantBackend.dbModel import Themes, ThemeDescriptors

    print("-> Creating theme data (=nmf data)")
    # Container dictionary to store configuration data
    configData_dict = {}
    # Container to store nmf_description data in a structure that makes input in the database easier
    nmfDescData_dict = {}

    # Fetch config files
    directory = os.fsencode('config')
    # Loop through files in config directory
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            # If the file is a json file then load it
            with open(os.path.join('config', filename)) as json_config_file:
                configData = json.load(json_config_file)
            # Assign a dictionary with matrix_file and desription_file in the configData_dict + location of the files
            configData_dict[language_dict[configData['general']['language']]] = {
                'location': configData['general']['data_directory'],
                'language': configData['general']['language'],
                'description_file': configData['nmf']['description_file']}

    # Loop the configData_dict and create the right structure
    for language in configData_dict:
        # Top-level iteration: we run through the xxxxx.json files
        NMF_DESCRIPTION_FILE = os.path.join(
            configData_dict[language]['location'],
            configData_dict[language]['language'],
            configData_dict[language]['description_file'])
        # Load the file
        with open(NMF_DESCRIPTION_FILE, 'rb') as f:
            nmf_descriptions = pickle.load(f, encoding='utf8')
        # Create the dictionary: key is the id in the first file,
        # data is a dictionary with language as key and the list of describing words as data
        for id in range(len(nmf_descriptions)):
            # Check if there is already an entry for this id in the top-level dict -> fetch or create an empty data dictionary
            if id in nmfDescData_dict.keys():
                dim_dict = nmfDescData_dict.get(id)
            else:
                nmfDescData_dict[id] = {}
            # Add the data to the dictionary
            nmfDescData_dict[id][language] = nmf_descriptions[id]

    # Now we have the nmf data in the correct structure
    # 1. We can check whether nmfDim points to the same translations of the their theme descriptors (=> they don't)
    # 2. We can decide change the datamodel (move the language column from theme descriptors to themes)
    # 3. We loop through our structure add the data to the database
    try:
        for nmfDim in nmfDescData_dict.keys():
            for lang in nmfDescData_dict[nmfDim].keys():
                th = db.session.query(Themes).filter_by(nmfDim=nmfDim, poemLanguage_id=lang).first()
                if not th:
                    th = Themes(nmfDim=nmfDim, poemLanguage_id=lang)
                    db.session.add(th)
                    db.session.flush()
                for order, (desc) in enumerate(nmfDescData_dict[nmfDim][lang], start=1):
                    thDesc = db.session.query(ThemeDescriptors).filter_by(theme_id=th.id, order=order).first()
                    if not thDesc:
                        thDesc = ThemeDescriptors(theme_id=th.id, themeDescriptor=desc, order=order)
                        db.session.add(thDesc)
        db.session.commit()
        db.session.expunge(th)
        db.session.expunge(thDesc)
    except IntegrityError as IErr:
        db.session.rollback()
        print("   <--- The theme data was already created: ", IErr.orig)
    except SQLAlchemyError as SErr:
        db.session.rollback()
        print("   <--- Error during creation of theme data: ", SErr.orig)
    except Exception as e:
        print("   <--- Unexpected error during creation of configuration data: ", e)
        print(traceback.format_exc())

    # Import parameter files
    print("-> Creating parameter data")
    from WritingAssistantBackend.dbModel import ConfigurationCategories, ConfigurationParameters

    # Fetch config files
    directory = os.fsencode('config')
    # Loop through files in config directory
    try:
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                # If the file is a json file then load it
                with open(os.path.join('config', filename)) as json_config_file:
                    configData = json.load(json_config_file)
                    language_id = poem_language_ids[language_dict[configData['general']['language']]]
                    for ckey, configCat in configData.items():
                        cat = db.session.query(ConfigurationCategories).filter_by(configurationCategory=ckey).first()
                        if not cat:
                            cat = ConfigurationCategories(configurationCategory=ckey)
                            db.session.add(cat)
                            db.session.flush()
                        for pkey, param in configCat.items():
                            par = db.session.query(ConfigurationParameters).filter_by(poemLanguage_id=language_id,
                                                                                      configurationCategory_id=cat.id,
                                                                                      parameter=pkey).first()
                            if not par:
                                par = ConfigurationParameters(poemLanguage_id=language_id,
                                                              configurationCategory_id=cat.id,
                                                              parameter=pkey,
                                                              value=param)
                                db.session.add(par)
        db.session.commit()
    except IntegrityError as IErr:
        db.session.rollback()
        print("   <--- The configuration data was already created: ", IErr.orig)
    except SQLAlchemyError as SErr:
        db.session.rollback()
        print("   <--- Error during creation of configuration data: ", SErr.orig)
        traceback.print_exc()
    except Exception as e:
        print("   <--- Unexpected error during creation of configuration data: ", e)
        print(traceback.format_exc())

    # Add actionTypes
    import csv
    from WritingAssistantBackend.dbModel import ActionTypes

    print("-> Creating action types")
    # Fetch config files
    directory = os.fsencode('data')
    # Loop through files in config directory
    try:
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith('.csv'):  # there will be only one csv file in the directory
                with open(os.path.join('data', filename), mode='r') as file:
                    csvFile = csv.DictReader(file, delimiter=';')
                    for row in csvFile:
                        AT = db.session.query(ActionTypes).filter_by(actionType=row['actionType'].strip()).first()
                        if not AT:
                            AT = ActionTypes(actionType=row['actionType'].strip(),
                                             actionTypeDescription=row['actionTypeDescription'].strip())
                            db.session.add(AT)
        db.session.commit()

    except IntegrityError as IErr:
        db.session.rollback()
        print("   <--- The configuration data was already created: ", IErr.orig)
    except SQLAlchemyError as SErr:
        db.session.rollback()
        print("   <--- Error during creation of configuration data: ", SErr.orig)
        traceback.print_exc()
    except Exception as e:
        print("   <--- Unexpected error during creation of configuration data: ", e)
        print(traceback.format_exc())

print("*** Finished importing initial data ***")
