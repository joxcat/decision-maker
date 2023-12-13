from collections import defaultdict
from lxml import etree as ET


class ObjectParser:
    def __init__(self, object_xml_file):
        self.object_file = object_xml_file
        self.tree = ET.parse(object_xml_file)

    def all_objects(self):
        all_objects = []
        root = self.tree.getroot()
        for obj in root.findall("./category/object"):
            all_objects.append(obj.attrib['name'])
        all_objects.sort(key=len)
        all_objects.reverse()
        return all_objects

    '''return dictionary mapping categories to items'''

    def get_categories_to_objects(self):
        root = self.tree.getroot()

        categories = {}
        for cat in root.findall("./category"):
            cat_name = cat.attrib['name'].lower()
            cat_objs = []
            for obj in cat.findall("object"):
                cat_objs.append(obj.attrib['name'].lower())
            categories[cat_name] = cat_objs
        return categories

    def get_objects_to_categories(self):
        categories = {}
        for cat in self.tree.findall("//category"):
            cat_name = cat.attrib['name'].lower()
            for obj in cat.findall("object"):
                obj_name = obj.attrib['name'].lower()
                categories[obj_name] = cat_name
        return categories

    def get_object_color(self, object_name):
        root = self.tree.getroot()
        for obj in root.findall("./category/object"):
            if obj.attrib['name'].lower() == object_name.lower():
                return obj.attrib['color']
        return None

    def get_attributes(self):
        all_obj = self.tree.findall("//object")
        attributes = defaultdict(lambda: defaultdict(None))
        for obj in all_obj:
            obj_name = obj.attrib["name"]
            obj_attr = obj.attrib
            for attr_name, value in obj_attr.items():
                if value.lower() in ["true", "false"]:
                    value = value.lower() == "true"
                # Attribute names are caseinsensitive
                attr_name = attr_name.lower()
                if attr_name == "name":
                    continue
                else:
                    attributes[attr_name][obj_name] = value
        return attributes


class LocationParser(object):
    def __init__(self, location_xml_file):
        self.location_file = location_xml_file
        self.tree = ET.parse(self.location_file)

    '''return dictionary of room:location_list'''

    def get_locations_in_room(self):
        room_locations = {}
        root = self.tree.getroot()
        for room in root.findall("./room"):
            location_list = []
            room_name = room.attrib['name'].lower()
            for thing in room:
                location_list.append(thing.attrib['name'].lower())
            room_locations[room_name] = location_list
        return room_locations

    def get_room_locations_are_in(self):
        mapping = {}
        root = self.tree.getroot()
        for room in root.findall("./room"):
            room_name = room.attrib['name'].lower()
            for thing in room:
                mapping[thing.attrib['name'].lower()] = room_name
        return mapping

    def get_all_locations(self):
        locations = []
        # For our purposes, rooms and locations are all locations
        for location in self.tree.findall("//location") + self.tree.findall("//room"):
            locations.append(location.attrib['name'])
        return locations

    def get_all_placements(self):
        all_placements = []
        root = self.tree.getroot()
        for location in root.findall("./room/location"):
            if 'isPlacement' in location.attrib:
                if location.attrib['isPlacement'] == "true":
                    all_placements.append(location.attrib['name'])
        return all_placements

    def get_all_beacons(self):
        all_beacons = []
        root = self.tree.getroot()
        for room in root.findall("./room"):
            for location in room:
                if 'isBeacon' in location.attrib:
                    if location.attrib['isBeacon'] == "true":
                        all_beacons.append(location.attrib['name'])
        return all_beacons

    def get_all_rooms(self):
        all_rooms = []
        for room in self.tree.findall("//room"):
            all_rooms.append(room.attrib['name'])
        return all_rooms

    def get_attributes(self):
        all_loc = self.tree.findall("//location") + self.tree.findall("//room")
        attributes = defaultdict(lambda: defaultdict(None))
        for loc in all_loc:
            loc_name = loc.attrib["name"]
            loc_attr = loc.attrib
            for attr_name, value in loc_attr.items():
                if value.lower() in ["true", "false"]:
                    value = value.lower() == "true"
                # Attribute names are caseinsensitive
                attr_name = attr_name.lower()
                if attr_name == "name":
                    continue
                else:
                    attributes[attr_name][loc_name] = value
            # Is there a room with this name?
            if loc.tag == "room":
                attributes["isroom"][loc_name] = True
        return attributes


class QuestionParser:
    def __init__(self, questions_xml_file):
        self.tree = ET.parse(questions_xml_file)

    def get_question_answer_dict(self):
        qa_dictionary = {}

        root = self.tree.getroot()
        for question in root.findall("./question"):
            question_text = ""
            answer_text = ""
            for child in question:
                if child.tag == "q":
                    question_text = child.text
                elif child.tag == "a":
                    answer_text = child.text
            qa_dictionary[question_text] = answer_text
        return qa_dictionary


class GesturesParser:
    def __init__(self, gestures_xml_file):
        self.tree = ET.parse(gestures_xml_file)

    def get_gestures(self):
        gestures = set()

        root = self.tree.getroot()
        for question in root.findall("./gesture"):
            gestures.add(question.attrib["name"])
        return gestures


class NameParser:
    def __init__(self, names_xml_file):
        self.tree = ET.parse(names_xml_file)

    def all_names(self):
        all_names = []
        root = self.tree.getroot()
        for name in root.findall("./name"):
            all_names.append(name.text)
        return all_names
