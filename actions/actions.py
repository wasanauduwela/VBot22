from typing import Text, List, Any, Dict
from owlready2 import *
from SPARQLWrapper import *
from tabulate import tabulate
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
)

class ActionBraCupFeatures(Action):

    def name(self) -> Text:
        return "action_exisitng_bracup_features"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

       # element_entity = str(tracker.get_slot("element"))
        element_entity = str(next(tracker.get_latest_entity_values("element"), None))
        element_name = str(tracker.get_slot("bra_name"))
        print(element_entity + "element")

        attribute_raw = []
        attribute_list =[]
        element_value = "false"
        attribute_value ="false"
        i=0
        ontology = get_ontology("file://TestingOntology.owl").load()
        graph = default_world.as_rdflib_graph()
        query = "SELECT DISTINCT ?p WHERE {?p rdf:type owl:Class.}"  # provide all the classes (Bra, BraCup, ..)
        r = list(graph.query_owlready("" + query + ""))
        for entity in r:
            tem_entity = (str(entity).replace(']', ''))
            tem_entity = tem_entity.replace('[', '')
            element = tem_entity.split(".")
            if element[1] == element_entity:
                element_value = "true"
                query = "SELECT ?instance WHERE {?instance rdf:type <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#" + element_entity + ">}"  # to take the instances of bra cup -> bracup_1, bracup_2
                r1 = list(graph.query_owlready("" + query + ""))
                query = "SELECT DISTINCT ?y WHERE {?p rdf:type owl:ObjectProperty. <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#"+ element_name+"> ?p ?y }"  # to take the related instances of purticulat instance
                r2 = list(graph.query_owlready("" + query + ""))
                for tem1 in r1:
                    for tem2 in r2:
                        if str(tem1) == str(tem2):
                            attribute_value = "true"
                            tem_instance = (str(tem1).replace(']', ''))
                            tem_instance = tem_instance.replace('[', '')
                            instance = tem_instance.split(".")
                            query = "SELECT DISTINCT ?q ?y WHERE {?p rdf:type owl:ObjectProperty. <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#" + instance[1] + \
                                    "> ?p ?y. ?y rdf:type ?q. ?q rdf:type owl:Class}"  # to take the related instances of purticulat instance
                            r = list(graph.query_owlready("" + query + ""))
                            for temp_at in r:
                                print(temp_at)
                                for tem_val in temp_at:
                                    print(tem_val)
                                    tem_val_element = (str(tem_val).replace(']', ''))
                                    tem_val_element = tem_val_element.replace('[', '')
                                    attribute = tem_val_element.split(".")
                                    attribute_raw.append(attribute[1])
                                print(attribute_raw)
                                attribute_list.append(attribute_raw[:])
                                print(attribute_list)
                                attribute_raw.clear()


                            dispatcher.utter_message(text="you can change the following values of the selected element as you wish. I will guide you for the selection.\n" +  tabulate(attribute_list,headers=['attributes', 'exisiting values']))


                            return [SlotSet("element", element_entity)]
                            break
                            # print (str(r))
                            # print(tabulate(r,headers=['attributes', 'exisiting values']))

        if element_value == "false":
            dispatcher.utter_message(text="Sorry. you have selected an incorrect element. Please select an element among BraCup, Fastening, Bottom Band, Cradle, Wing, Back style, Fabric, Easthetic as you wish")
            return [SlotSet("element", None)]
        if attribute_value == "false":
            dispatcher.utter_message(text="There are no any attribute related to the element")
            return [SlotSet("element", None)]


class ValidateSimpleBraForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_bra_form"

    def validate_bra_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `bra_name` value."""

        haveBra = "false"
        sportImapct = ""
        equal_impact = ""
        impact_levels_sport = ""
        impact_levels_bra=""
        trueBraName = ""

        #to take sport
        sport = tracker.get_slot("sport_name")

        # to take bra name
        onto = get_ontology("file://TestingOntology.owl").load()
        for i in onto.Bra.instances():
            temBraName = str(i).split(".")
            if temBraName[1] == str(slot_value):
                haveBra = "true"
                trueBraName = str(slot_value)

        if haveBra == "true" and sport != None:
            graph = default_world.as_rdflib_graph()
            query = "SELECT ?impactlevel {<http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#" + trueBraName + "> <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#hasImpactLevel> ?impactlevel.}"
            r = list(graph.query_owlready("" + query + ""))
            for tem_impact in r:
                tem_impact_string = (str(tem_impact).replace(']', ''))
                tem_impact_string = tem_impact_string.replace('[', '')
                impact = tem_impact_string.split(".")
                if len(r) > 1:
                    impact_levels_bra = str(impact[1]) + ", " + impact_levels_bra
                elif len(r) == 1:
                    impact_levels_bra = str(impact[1])

            graph = default_world.as_rdflib_graph()
            query = "SELECT ?impactlevel {<http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#" + str(sport).title() + "> <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#requiredImpactLevel> ?impactlevel.}"
            r = list(graph.query_owlready("" + query + ""))
            for tem_impact in r:
                tem_impact_string = (str(tem_impact).replace(']', ''))
                tem_impact_string = tem_impact_string.replace('[', '')
                impact = tem_impact_string.split(".")
                impact_levels_sport = str(impact[1]) + ", " + impact_levels_sport

            if len(impact_levels_sport.split(",")) > 1 and len(impact_levels_bra.split(",")) > 1:
                impact_levels_sport_array = impact_levels_sport.split(",")
                impact_levels_bra_array = impact_levels_bra.split(",")
                for sport_impact in impact_levels_sport_array:
                    for bra_impact in impact_levels_bra_array:
                        if sport_impact == bra_impact and sport_impact != "":
                            equal_impact = sport_impact + equal_impact + ","
            if len(impact_levels_sport.split(",")) > 1 and len(impact_levels_bra.split(",")) == 1:
                impact_levels_sport_array = impact_levels_sport.split(",")
                for sport_impact in impact_levels_sport_array:
                    if sport_impact == impact_levels_bra:
                        equal_impact = sport_impact
            if len(impact_levels_sport.split(",")) == 1 and len(impact_levels_bra.split(",")) > 1:
                impact_levels_bra_array = impact_levels_bra.split(",")
                for bra_impact in impact_levels_bra_array:
                    if bra_impact == impact_levels_sport:
                        equal_impact = bra_impact

            if equal_impact == "":
                print("nonsence")
                dispatcher.utter_message(text=f"The selected bra is not match with the impact level of the sport you are doing. Please select a bra with " + impact_levels_sport)
                return {"bra_name": None}
            else:
                dispatcher.utter_message(text=f"OK! You have selected {slot_value} bar. And it's impact level also compatible with the sport you are doing")
                {"sport_impact": impact_levels_sport}
                {"sport_name": str(sport).title()}
                {"bra_name": slot_value}
                return {"bra_impact": impact_levels_bra}

        elif haveBra == "true" and sport == None:
            onto = get_ontology("file://TestingOntology.owl").load()
            graph = default_world.as_rdflib_graph()
            query = "SELECT ?impactlevel {<http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#" + trueBraName + "> <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#hasImpactLevel> ?impactlevel.}"
            r = list(graph.query_owlready("" + query + ""))
            for tem_impact in r:
                tem_impact_string = (str(tem_impact).replace(']', ''))
                tem_impact_string = tem_impact_string.replace('[', '')
                impact = tem_impact_string.split(".")
                if len(r) > 1:
                    impact_levels_bra = str(impact[1]) + ", " + impact_levels_bra
                elif len(r) == 1:
                    impact_levels_bra = str(impact[1])
            dispatcher.utter_message(text=f"What is the sport you are doing? ")
            return {"bra_impact": impact_levels_bra}

        elif (haveBra == "" and sport == None) or (haveBra == "" and sport != None):
            dispatcher.utter_message(text=f"I don't recognize that bra. Please select a correct one from the list")
            return {"bra_name": None}

    def validate_sport_name(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `sport_name` value."""

        haveSport = "false"
        impact_levels = ""
        impact_levels_bra = ""
        impact_levels_sport = ""
        equal_impact = ""

        #to get the bra name
        bra = tracker.get_slot("bra_name")
        print(bra)

        #to get the sport name
        onto = get_ontology("file://TestingOntology.owl").load()
        for i in onto.Sports.instances():
            temSportName = str(i).split(".")
            if temSportName[1] == str(slot_value).title():
                haveSport = "true"

        if haveSport == "true" and bra != None:
            onto = get_ontology("file://TestingOntology.owl").load()
            graph = default_world.as_rdflib_graph()
            query = "SELECT ?impactlevel {<http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#" + str(bra) + "> <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#hasImpactLevel> ?impactlevel.}"
            r = list(graph.query_owlready("" + query + ""))
            for tem_impact in r:
                tem_impact_string = (str(tem_impact).replace(']', ''))
                tem_impact_string = tem_impact_string.replace('[', '')
                impact = tem_impact_string.split(".")
                if len(r) > 1:
                    impact_levels_bra = str(impact[1]) + ", " + impact_levels_bra
                elif len(r) == 1:
                    impact_levels_bra = str(impact[1])

            graph = default_world.as_rdflib_graph()
            query = "SELECT ?impactlevel {<http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#" + str(
                slot_value).title() + "> <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#requiredImpactLevel> ?impactlevel.}"
            r = list(graph.query_owlready("" + query + ""))
            for tem_impact in r:
                tem_impact_string = (str(tem_impact).replace(']', ''))
                tem_impact_string = tem_impact_string.replace('[', '')
                impact = tem_impact_string.split(".")
                impact_levels_sport = str(impact[1]) + ", " + impact_levels_sport

            if len(impact_levels_sport.split(",")) > 1 and len(impact_levels_bra.split(",")) > 1:
                impact_levels_sport_array = impact_levels_sport.split(",")
                impact_levels_bra_array = impact_levels_bra.split(",")
                for sport_impact in impact_levels_sport_array:
                    for bra_impact in impact_levels_bra_array:
                        if sport_impact == bra_impact and sport_impact != "":
                            equal_impact = sport_impact + equal_impact + ","
            if len(impact_levels_sport.split(",")) > 1 and len(impact_levels_bra.split(",")) == 1:
                impact_levels_sport_array = impact_levels_sport.split(",")
                for sport_impact in impact_levels_sport_array:
                    if sport_impact == impact_levels_bra:
                        equal_impact = sport_impact
            if len(impact_levels_sport.split(",")) == 1 and len(impact_levels_bra.split(",")) > 1:
                impact_levels_bra_array = impact_levels_bra.split(",")
                for bra_impact in impact_levels_bra_array:
                    if bra_impact == impact_levels_sport:
                        equal_impact = bra_impact
            print(impact_levels_sport)
            print(impact_levels_bra)
            print(equal_impact)
            if equal_impact == "":
                dispatcher.utter_message(text=f"The selected bra is not match with the impact level of the sport you are doing. Please select a bra with " + impact_levels_sport)
                {"sport_name": impact_levels_sport}
                return {"bra_name": None}
            else:
                dispatcher.utter_message(
                    text=f"OK! You have selected {slot_value} bar. And it's impact level also compatible with the sport you are doing")
                {"sport_impact": impact_levels_sport}
                {"sport_name": slot_value}
                {"bra_name": str(bra)}
                return {"bra_impact": impact_levels_bra}

        elif haveSport == "true" and bra == None:
            graph = default_world.as_rdflib_graph()
            query = "SELECT ?impactlevel {<http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#" + str(
                slot_value).title() + "> <http://www.semanticweb.org/wasanauduwela/ontologies/2022/11/TestingOntology#requiredImpactLevel> ?impactlevel.}"
            r = list(graph.query_owlready("" + query + ""))
            for tem_impact in r:
                tem_impact_string = (str(tem_impact).replace(']', ''))
                tem_impact_string = tem_impact_string.replace('[', '')
                impact = tem_impact_string.split(".")
                impact_levels_sport = str(impact[1]) + ", " + impact_levels_sport
            dispatcher.utter_message(text=f"What is the selected sports bra?")
            return {"sport_impact": impact_levels_sport}

        elif (haveSport != "true" and bra == None) or  (haveSport != "true" and bra != None):
            dispatcher.utter_message( text=f"We only accept sport: yoga, zumba, aerobic, jogging, gym, work out from home")
            return {"sport_name": None}











