from sqlalchemy import func, desc

from .dbModel import Poem as PoemModel, PoemLanguage, RhymeScheme, RhymeSchemeElement, ConfigurationCategory, \
    ConfigurationParameter
from .extensions import db


class PoembaseConfig:

    # Returns the data for populating drop-downs in the interface
    @staticmethod
    def webLists():
        return [{"lang": {
            "label": "Language: ",
            "options": PoembaseConfig.PoemLanguages.getList()}},
            {"form": {
                "label": "Rhyme scheme: ",
                "options": PoembaseConfig.Poemforms.getList()}}]

    @staticmethod
    def getParameter (language: int, category:str, parameterName:str):
        parameter = (db.session.query(ConfigurationParameter).
                     join(ConfigurationCategory, ConfigurationParameter.configurationCategory_id == ConfigurationCategory.id).
                     filter(ConfigurationParameter.poemLanguage_id == language).
                     filter(ConfigurationParameter.parameter == parameterName).
                     filter(ConfigurationCategory.configurationCategory == category).first())  # there will be one and only one element
        return parameter.value

    # Class for handling poemlanguages
    class PoemLanguages:

        # Returns a list of the available poem languages;
        # put 'default' flag on the language most frequently chosen by the user
        @staticmethod
        def getList():
            # Look for the default: the language in which the user has written the most poems
            dflt = (db.session.query(PoemModel.poemLanguage_id.label("language_id"),
                                    func.count(PoemModel.poemLanguage_id).label("count"))
                                        .filter(PoemModel.user_id == 1).group_by(PoemModel.poemLanguage_id)
                                        .order_by(desc("count"))
                                        .limit(1)
                                        .one_or_none())

            languages = db.session.query(PoemLanguage).distinct().all()
            output = []
            for l in languages:
                l_out = {"id":l.id, "label":l.label}
                if dflt is not None:
                    if l.id == dflt.language_id:
                        l_out.update({"default":True})
                output.append(l_out)
            return output
    # Class for handling the rhyme schemes
    class Poemforms:
        # Returns a list of available rhyme schemes
        @staticmethod
        def getList():
            # Look for the default: the language in which the user has written the most poems
            schemes = (db.session.query(RhymeScheme).all())

            output = []
            for RS in schemes:
                rs_out = {"id":RS.id, "label":RS.rhymeScheme }
                if RS.persistent:
                    rs_out.update({"persistent":True})
                output.append(rs_out)
            return output

        @staticmethod
        def queryElements(lang,form):
            return (db.session.query(RhymeSchemeElement.id, RhymeSchemeElement.rhymeSchemeElement).
                        filter(RhymeSchemeElement.poemLanguage_id == lang).
                        filter(RhymeSchemeElement.rhymeScheme_id == form).
                        order_by(RhymeSchemeElement.order.asc()).
                        all())
        @staticmethod
        def getElements(lang, form):
            elem_out = []
            elements = PoembaseConfig.Poemforms.queryElements(lang=lang, form=form)
            for e in elements:
                elem_out.append(e.rhymeSchemeElement)
            return tuple(elem_out)
        @staticmethod
        def webElements(lang,form):
            elements = PoembaseConfig.Poemforms.queryElements(lang=lang, form=form)
            outputList = []
            for e in elements:
                outputList.append({'verse':{'id':e.id,'txt':e.rhymeSchemeElement}})
            output = {'id':form,'elements':outputList}
            return output