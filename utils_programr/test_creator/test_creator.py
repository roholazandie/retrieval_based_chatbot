import xml.etree.ElementTree as ET
import sys
from programr.parser.template.nodes.bot import TemplateBotNode
from programr.parser.template.nodes.get import TemplateGetNode
from programr.clients.client import BotClient
from programr.clients.events.console.config import ConsoleConfiguration

class TestCreatorBotClient(BotClient):

    def __init__(self):
        super().__init__("TestCreator")

    @property
    def test_dir(self):
        return self.arguments.args.test_dir

    @property
    def test_file(self):
        return self.arguments.args.test_file

    @property
    def qna_file(self):
        return self.arguments.args.qna_file

    @property
    def verbose(self):
        return self.arguments.args.verbose

    def get_description(self):
        return 'ProgramR Test Creator Client'

    def add_client_arguments(self, parser=None):
        if parser is not None:
            parser.add_argument('--aiml_file', dest='aiml_file', help='AIML File to create tests from')
            parser.add_argument('--test_file', dest='test_file', help='Test file to create with associated unit tests')
            parser.add_argument('--ljust', dest='ljust', action='store_true', help='Left justifies the first csv column, a good value is 40 or 80')
            parser.add_argument('--replace_file', dest='replace_file', help='When creating tests you can specify replacements certain data types')

    def get_client_configuration(self):
        return ConsoleConfiguration()
            

def load_replacements(replace_file):
    texts = {}
    bots = {}
    sets = {}
    with open(replace_file, "r") as file:
        for line in file:
            line = line.strip()
            name_value = line.split(":")
            type_name = name_value[0].split(",")
            if len(type_name) == 2:
                if type_name[0] == "SET":
                    sets[type_name[1]] = name_value[1].upper()
                elif type_name[0] == "BOT":
                    bots[type_name[1]] = name_value[1].upper()
                else:
                    print("Unknown mapping type", type_name[0].upper())
            else:
                texts[type_name[0]] = name_value[1]

    return texts, sets, bots

def replace_wildcard(text, texts, wildcard):
    if wildcard in text and wildcard in texts:
        return text.replace(wildcard, texts[wildcard])
    return text

def replace_wildcards(text, texts):
    text = replace_wildcard(text, texts, "*")
    text = replace_wildcard(text, texts, "#")
    text = replace_wildcard(text, texts, "^")
    text = replace_wildcard(text, texts, "_")
    return text

def parse_lis(elt):
    lis = elt.findall("li")
    random_string = ""
    bot_tail = None
    get_tail = None
    for li in lis:
        # print("li: {}".format(type(li)))
        li_string = ""
        for elem in li.iter():
            # print("elem: {} - {}".format(elem.tag, type(elem)))
            
            if elem.tag == "bot":
                # print("Found bot tag!")
                li_string += " " + bot_node.get_bot_variable(client_context, elem.attrib['name'])
                if elem.tail is not None:
                    bot_tail = elt.tail.strip()

            elif elem.tag == "get":
                # print("Found get tag!")
                li_string += " " + get_node.get_property_value(client_context, False, elem.attrib['name'])
                if elem.tail is not None:
                    get_tail = elem.tail.strip()

        if li.text is not None:
            random_string += li.text.strip()
            # print("random_string with added li.text: {}".format(random_string))
            if bot_tail is not None and get_tail is not None:
                # print("Both are not none")
                random_string += li_string + bot_tail.strip() + get_tail.strip()
                # print("random_string: {}".format(random_string))
            
            elif bot_tail is not None and get_tail is None:
                # print("bot is not none")
                # print("bot_tail: {}".format(bot_tail))
                # print("li_string: {}".format(li_string))
                # print("random_string: {}".format(random_string))
                random_string += li_string + bot_tail.strip()
                # print("random_string: {}".format(random_string))

            elif bot_tail is None and get_tail is not None:
                # print("get is not none")
                random_string += li_string + get_tail.strip()
            
            else:
                pass
                # print("in else, do nothing...")
                # random_string += li.text.strip()
                # print("random_string: {}".format(random_string))

        random_string += "; "
                
    # print("Cleaning string")
    random_string = random_string[:-2]
    random_string += "]"
    # print("random_string: {}".format(random_string))

    return random_string

def check_for_think(template):
    thinks = template.findall("think")

    if thinks is None:
        return template

    else:
        # template_list = list(template.iter())
        # print("template before removing think: {}".format(template_list))
        for think in thinks:
            text = think.tail.strip()
            template.remove(think)
            if text is not None:
                if template.text is None:
                    template.text = text
                else:
                    template.text += text
            # template_list = list(template.iter())
            # print("template after removing think: {}".format(template_list))
        return template


def parse_categories(categories, output_file, bot_node, get_node, aiml_file, texts):
    try:
        seen = set()
        questions = []
        for category in categories:
            pattern_text = ""
            random_exists = False

            pattern = category.find("pattern")
            for elt in pattern.iter():

                if elt.tag == "pattern":
                    text = elt.text.strip().upper()
                    if replace_wildcards(text, texts) is not None:
                        pattern_text += replace_wildcards(text, texts)

                elif elt.tag == "set":
                    if 'name' in elt.attrib:
                        name = elt.attrib['name']
                    else:
                        name = elt.text.strip()

                    if name in sets:
                        pattern_text += sets[name]
                    else:
                        pattern_text += "SET[%s]"%name

                elif elt.tag == "bot":
                    if 'name' in elt.attrib:
                        name = elt.attrib['name']
                    else:
                        name = elt.text.strip()

                    if name in bots:
                        pattern_text += bots[name]
                    else:
                        pattern_text += "BOT[%s]" % name
                
                # NOTE: Is this condition needed?
                elif elt.tag == "topic":
                    pass
                    # topic_cats = elt.tag.findall("category")
                    # topic_questions = parse_categories(topic_cats, output_file, bot_node, get_node, aiml_file)

                
                pattern_text += " "

                if elt.tail is not None and elt.tail.strip() != "":
                    text = elt.tail.strip().upper()
                    pattern_text += replace_wildcards(text, texts)
                    pattern_text += " "
            
            question = '"%s",'%pattern_text.strip()
            question = question.ljust(ljust)
                    
            template = category.find('template')
            template = check_for_think(template)

            string = ""
            tail = ""
            for elt in template.iter(): 
                tag = elt.tag
                try:
                    etl_tail = elt.tail.strip()
                except:
                    etl_tail = None
                
                if tag == "bot":
                    string = " " + bot_node.get_bot_variable(client_context, elt.attrib['name'])
                    if etl_tail is not None:
                        tail += etl_tail
                        # print("bot tail: {}".format(tail))

                elif tag == "get":
                    string = " " + get_node.get_property_value(client_context, False, elt.attrib['name'])
                    if etl_tail is not None:
                        tail += etl_tail
                        # print("get tail: {}".format(tail))

                elif tag == "set":
                    if elt.text is not None:
                        string = elt.text + " "
                    if etl_tail is not None:
                        tail += etl_tail
                        # print("set tail: {}".format(tail))
                
                elif tag == "random":
                    random_exists = True
                    random_string = parse_lis(elt)

                elif tag == "condition":
                    random_exists = True
                    random_string = parse_lis(elt)

                elif tag == "think":
                    if etl_tail is not None:
                        tail += etl_tail
                        # print("think tail: {}".format(tail))
                
                elif tag == "srai":
                    string = "<srai>" + elt.text + "</srai>"
                    if etl_tail is not None:
                        tail += etl_tail
                        # print("srai tail: {}".format(tail))


            # if len(li) > 0:
            #     test_line = '%s "%s"'%(question, string)
            # else:
            #     test_line = '%s "%s"'%(question, template.text)

            # print("tail after of the loop: {}".format(tail))
            
            try:
                template_text = template.text.strip()
            except Exception:
                template_text = None
            if random_exists:
                if template_text is None:
                    response = "[" + string + random_string
                else:
                    if tail is not None:
                        # print("there is a tail")
                        response = template_text + "[" + string + random_string + tail
                    else:
                        # print("tail is None")
                        response = template_text + "[" + string + random_string
                        # print("response: {}".format(response))
                    # print("test_line: {}".format(test_line))
            else:
                if template_text is None:
                    if tail is not None:
                        response = string + tail
                    else:
                        response = string
                else:
                    if tail is not None:
                        response = template_text + string + tail
                    else:
                        response = template_text + string
                        # print("response: {}".format(response))
                    
                    # print("test_line: {}".format(test_line))
            
            test_line = '%s "%s"'%(question, response)
            output_file.write(test_line)
            output_file.write("\n")

            f = open("results/questions.txt", "a")
            f.write(question + "\n")

            if response[0:6] != "<srai>" and response.lower() not in seen and response.lower().strip() is not "unknown":
                # seen = write_responses(response, seen)
                f = open("results/responses.txt", "a")
                f.write(response + "\n")
                response = response.lower()
                seen.add(response)
                
            
        print("completed")
        return questions

    except Exception as e:
            print(e)
            print(type(e))
            line = "failed to load file: " + aiml_file + "..." + str(e) + "\n"
            f = open("results/failed_loads.txt", "a")
            f.write(line)
            f.close()

def write_responses(response, seen):
    with open("results/responses.txt", "a") as f:
        for line in f:
            line_lower = line.lower()
            if line_lower in seen:
                f.write("")
            else:
                seen.add(line_lower)
                f.write(response + "\n")
    return seen

if __name__ == '__main__':

    aiml_file = sys.argv[4]
    test_file = sys.argv[6]
    # ljust = int(sys.argv[3])
    ljust = 20
    replace_file = sys.argv[8]

    print("aiml_file: {}".format(aiml_file))
    print("test_file: {}".format(test_file))
    print("ljust: {}".format(ljust))
    print("replace_file: {}".format(replace_file))

    client = TestCreatorBotClient()
    client_context = client.create_bot(1, load_variables=False)
    bot_node = TemplateBotNode()
    get_node = TemplateGetNode()

    default = None
    # if len(sys.argv) > 5:
    #     default = sys.argv[5]

    print("loading in file: " + aiml_file + "...")
    # print("test_file:", test_file)
    # print("replace_file:", replace_file)
    # print("Default:", default)

    texts, sets, bots = load_replacements(replace_file)

    with open(test_file, "w+") as output_file:
        # if default is not None:
        #     output_file.write('$DEFAULT, "%s"\n\n'%default)
        try:
            tree = ET.parse(aiml_file)
            aiml = tree.getroot()
            categories = aiml.findall('category')
            # print("categories: {}".format(type(categories)))
            
            topic = aiml.find('topic')
            if topic is not None:
                topic_categories = topic.findall('category')
            # categories += topic_categories

            questions = parse_categories(categories, output_file, bot_node, get_node, aiml_file, texts)

            if topic is not None:
                questions = parse_categories(topic_categories, output_file, bot_node, get_node, aiml_file, texts)

        except Exception as e:
            print(e)
            line = "failed to load file: " + aiml_file + "..." + str(e) + "\n"
            f = open("results/failed_loads.txt", "a")
            f.write(line)
            f.close()
        
        exit(0)