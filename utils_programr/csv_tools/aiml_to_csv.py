import sys
import xml.etree.ElementTree as ET
import csv
import re

class AIMLToCSVGenerator(object):

    def __init__(self):
        self._input = sys.argv[1]
        self._output = sys.argv[2]
        try:
            self._append = sys.argv[3]
        except:
            print("no file permission passed, defaulting to w+")
            self._append = None

    def run(self):
        csv_file = None
        if self._append is None:
            self._append = "w+"

        try:
            tree = ET.parse(self._input)
            csv_file = open(self._output, self._append)
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            root = tree.getroot()
            for element in root:
                if element.tag == 'category':
                    self.parse_category_to_file(csv_writer, element, topic="*")
                elif element.tag == 'topic':
                    for child in element:
                        if child.tag == 'category':
                            self.parse_category_to_file(csv_writer, child, topic=element.attrib['name'])

        except Exception as excep:
            print (excep)
        finally:
            if csv_file is not None:
                csv_file.flush()
                csv_file.close ()

    def parse_category_to_file(self, csv_writer, category, topic):
        pattern = None
        li_list = []
        that = "*"
        template = None
        random_exists = False
        for element in category:
            if element.tag == 'pattern':
                pattern = AIMLToCSVGenerator.element_to_string(element)
            elif element.tag == 'that':
                that = element.text
            elif element.tag == 'template':
                random_exists = self.check_random(element)
                if random_exists:
                    for sub_element in element:
                        if sub_element.tag == 'random' or sub_element.tag == 'condition':
                            for li_element in sub_element:
                                li_list.append(AIMLToCSVGenerator.element_to_string(li_element))
                else:
                    template = AIMLToCSVGenerator.element_to_string(element)

        pattern = AIMLToCSVGenerator.strip_all_whitespace(pattern, column="pattern")
        if template is not None:
            template = AIMLToCSVGenerator.strip_all_whitespace(template, column="template")
        topic = AIMLToCSVGenerator.strip_all_whitespace(topic)
        that = AIMLToCSVGenerator.strip_all_whitespace(that)

        if random_exists:
            try:
                for li in li_list:
                    li = AIMLToCSVGenerator.strip_all_whitespace(li, column="template")
                    csv_writer.writerow([pattern, topic, that, li])        
            except Exception as ex:
                print("Error writing random elements to file - ".format(ex))
        else:
            csv_writer.writerow([pattern, topic, that, template])

    def check_random(self, element):
        for sub_element in element:
            if sub_element.tag == 'random' or sub_element.tag == 'condition':
                return True
        return False

    @staticmethod
    def element_to_string(element):
        try:
            s = element.text or ""
            for sub_element in element:
                s += ET.tostring(sub_element).decode("utf-8")
            s += element.tail
            return s
        except Exception as ex:
            print("Error in element to string - {}".format(ex))
            return s

    @staticmethod
    def strip_all_whitespace(string, column=None):
        first_pass = re.sub(r'[\n\t\r+]', '', string)
        second_pass = re.sub(r'\s+', ' ', first_pass)
        if column == "template":
            think_removed = re.sub(r'<think>.*</think>', '', second_pass)
            robot_removed = re.sub(r'<oob>.*</oob>', '', think_removed)
            set_removed = re.sub(r'<set name=.*">', '', robot_removed) 
            set_removed = re.sub(r'</set>', '', set_removed)
            wildcardremoved = re.sub(r'\*', '[MASK]', set_removed)
            wildcardremoved = re.sub(r'\^', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'\_', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'\#', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'<star />', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'<star index=\".*\"\s*\/>', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'<that index=\".*\"\s*\/>', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'<input index=\".*\"\s*\/>', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'<person index=\".*\"\s*\/>', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'<get name=\".*\"\s*\/>', '[MASK]', wildcardremoved)
            return wildcardremoved.strip()
        elif column == "pattern":
            yes_set_removed = re.sub(r'\# <set>YES<\/set> \^', "YES", second_pass)
            no_set_removed = re.sub(r'\# <set>NO<\/set> \^', "NO", yes_set_removed)
            dont_set_removed = re.sub(r'\# <set>DON T KNOW<\/set> \^', "DON T KNOW", no_set_removed)
            wildcardremoved = re.sub(r'\*', '[MASK]', dont_set_removed)
            wildcardremoved = re.sub(r'\^', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'\_', '[MASK]', wildcardremoved)
            wildcardremoved = re.sub(r'\#', '[MASK]', wildcardremoved)
            return wildcardremoved.strip()
        else:
            return second_pass.strip()

if __name__ == '__main__':

    def run():
        print("Convertin AIML to CSV...")
        generator = AIMLToCSVGenerator()
        generator.run()

    run()
