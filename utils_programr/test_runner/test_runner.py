import csv
import re
import datetime
import os

from programr.clients.client import BotClient
from programr.utils.files.filefinder import FileFinder
from programr.clients.events.console.config import ConsoleConfiguration
# from programr.utils.logging.ylogger import YLogger

class TestQuestion(object):

    def __init__(self, question, answers, topic=None, that=None):
        self._category = None
        self._question = question
        self._answers = answers
        self._answers_regex = []
        self._topic = topic
        self._that = that
        for answer in answers:
            if answer is not None and answer:
                if answer[0] == "!":
                    self._answers_regex.append(("-", re.compile(answer)))
                else:
                    self._answers_regex.append(("+", re.compile(answer)))
        self._response = None

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        self._category = category

    @property
    def question(self):
        return self._question

    @property
    def answers(self):
        return self._answers

    @property
    def answers_regex(self):
        return self._answers_regex

    @property
    def answers_string(self):
        return " or ".join(self._answers)

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response

    @property
    def topic(self):
        return self._topic

    @property
    def that(self):
        return self._that

class TestFileFileFinder(FileFinder):

    def __init__(self):
        super().__init__()

    def empty_row(self, row):
        return bool(len(row) < 2)

    def is_comment(self, question):
        return bool(question[0] == '#')

    def is_template(self, question):
        return bool(question[0] == '$')

    def clean_up_answer(self, text):
        return text.replace('"', "").strip()

    def add_answers_to_template(self, row, question, templates):
        answers = []
        for answer in row[1:]:
            answers.append(self.clean_up_answer(answer))
        templates[question] = answers

    def add_template_answers(self, templates, answer, answers):
        if answer in templates:
            template = templates[answer]
            for template_answer in template:
                answers.append(template_answer)
        else:
            print("Template [%s] not found!" % answer)

    def load_file_contents(self, filename, userid="*"):
        print("Loading aiml_tests from file [%s]" % filename)
        questions = []
        templates = {}
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                if self.empty_row(row) is False:
                    question = row[0]
                    if self.is_comment(question) is False:
                        if self.is_template(question):
                            self.add_answers_to_template(row, question, templates)
                        else:
                            answers = []
                            that = None
                            topic = None
                            for answer in row[1:]:
                                answer = answer.strip()
                                if answer:
                                    if self.is_template(answer):
                                        self.add_template_answers(templates, answer, answers)
                                    else:
                                        if answer.startswith("\"THAT="):
                                            thatsplits = self.clean_up_answer(answer).split("=")
                                            that = thatsplits[1]
                                        elif answer.startswith("\"TOPIC="):
                                            topicsplits = self.clean_up_answer(answer).split("=")
                                            topic = topicsplits[1]
                                        else:
                                            answers.append(self.clean_up_answer(answer))
                            questions.append(TestQuestion(question, answers, topic=topic, that=that))
        return questions


    def get_just_filename_from_filepath(self, filepath):

        if os.sep in filepath:
            pathsplits = filepath.split(os.sep)
            filename_ext = pathsplits[-1]
        else:
            filename_ext = filepath

        if "." in filename_ext:
            filesplits = filename_ext.split(".")
            filename = filesplits[0]
        else:
            filename = filename_ext

        return filename

    def find_files(self, path, subdir=False, extension=None):
        # print("Path: {}".format(path))
        found_files = []
        try:
            if subdir is False:
                paths = os.listdir(path)
                for filename in paths:
                    if filename.endswith(extension):
                        found_files.append((filename, os.path.join(path, filename)))
            else:
                for dirpath, _, filenames in os.walk(path):
                    # print("filenames: {}".format(filenames))
                    for filename in [f for f in filenames if f.endswith(extension)]:
                        found_files.append((filename, os.path.join(dirpath, filename)))
        except FileNotFoundError:
            # YLogger.error(self, "No directory found [%s]", path)
            a = 0

        return sorted(found_files, key=lambda element: (element[1], element[0]))

    def load_dir_contents(self, paths, subdir=False, extension=".txt", filename_as_userid=False):
        # print("Paths: {}".format(paths))
        # print("Subdir: {}".format(subdir))
        files = self.find_files(paths, subdir, extension)
        # print("Files: {}".format(files))

        collection = {}
        file_maps = {}
        num = 0
        for file in files:
            just_filename = self.get_just_filename_from_filepath(file[0])
            try:
                if filename_as_userid:
                    userid = just_filename
                else:
                    userid = "*"
                # print("#################file[1]: {}".format(file[1]))
                collection[just_filename.upper()] = self.load_file_contents(file[1], num)
                file_maps[just_filename.upper()] = file[1]
                num += 1
            except Exception as excep:
                print(excep)
                # YLogger.exception(self, "Failed to load file contents for file [%s]"% file[1], excep)

        return collection, file_maps


    def load_single_file_contents(self, filename):
        just_filename = self.get_just_filename_from_filepath(filename)

        collection = {}
        file_maps = {}
        try:
            collection[just_filename.upper()] = self.load_file_contents(filename)
            # file_maps[just_filename.upper()] = filename
        except Exception as excep:
            print(excep)
            # YLogger.exception(self, "Failed to load file contents for file [%s]"%filename, excep)

        return collection, file_maps


class TestRunnerBotClient(BotClient):

    def __init__(self):
        super().__init__("TestRunner")

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
        return 'ProgramR Test Runner Client'

    def ask_question(self, userid, question):
        response = ""
        try:
            client_context = self.create_bot(userid)
            response = client_context.bot.ask_question(client_context, question)
            response = self.remove_oob(response)
            return response
        except Exception as e:
            print(e)
            return ""
        
    def remove_oob(self, response):
        return re.sub('<oob><robot></robot></oob>', '', response)

    def add_client_arguments(self, parser=None):
        if parser is not None:
            parser.add_argument('--test_dir', dest='test_dir', help='directory containing test files to run against grammar')
            parser.add_argument('--test_file', dest='test_file', help='Single file of aiml_tests to run against grammar')
            parser.add_argument('--qna_file', dest='qna_file', help='A file containing questions and answers')
            parser.add_argument('--verbose', dest='verbose', action='store_true', help='print out each question to be asked')

    def set_environment(self):
        self.bot.brain.properties.add_property("env", "TestRunner")

    def get_client_configuration(self):
        return ConsoleConfiguration()

    def write_to_file(self, tag, filename):
        line = "\t%s: [%s] expected [%s], got [%s]\n" % (tag.category, tag.question, tag.answers_string, tag.response)
        s = "results/" + filename
        f = open(s, "a")
        f.write(line)
        f.close()

    def run(self):
        file_finder = TestFileFileFinder()
        if self.test_dir is not None:
            print("Loading Tests from directory [%s]" % self.test_dir)
            questions = file_finder.load_dir_contents(self.test_dir, extension=".tests", subdir=False)
        else:
            print("Loading single file: {}".format(self.test_file))
            questions = file_finder.load_single_file_contents(self.test_file)

        question_and_answers = open(self.qna_file, "w+")
        # print("Question and answers: {}.".format(type(question_and_answers)))

        # out = dict(list(questions[1].keys())[0: 2])

        successes = []
        failures = []
        warnings = 0
        start = datetime.datetime.now()
        # print("Questions: {}".format(type(questions[0])))
        # print("Questions: {}".format(questions[0]))
        # print("Questions: {}".format(type(questions[1])))
        # print("Questions: {}".format(out))
        # print("Other: {}".format(other))
        for category in questions[0].keys():
            for test in questions[0][category]:
                test.category = category
                
                # TODO: Still need way to handle srai tag
                # print("test.answers_regex: {}".format(test.answers_regex[0][1].pattern))
                # # print("test.answers_regex[0][1]: {}".format(type(test.answers_regex[0][1])))
                # pattern = test.answers_regex[0][1].pattern
                # if pattern[0:6] == "<srai>":
                #     print("SRAI tag detected!!")
                #     test.answers_regex[0][1].pattern = re.sub('<srai>', '', pattern)
                #     print("test.answers_regex after removal: {}".format(test.answers_regex[0][1]))

                if any((c in '$*_^#') for c in test.question):
                    try:
                        test.question = test.question.replace("", any((c in '$*_^#')))
                    except Exception as e:
                        print("WARNING: Wildcards in question! [%s]"%test.question)
                        warnings = warnings +1

                if test.topic is not None:
                    conversation = self.get_conversation(0)
                    conversation.set_property("topic", test.topic)

                if test.that is not None:
                    response = self.ask_question(0, test.that)
                else:
                    response = self.ask_question(0, test.question)
    
                success = False
                test.response = response

                if self.verbose:
                    print(test.question, "->", test.response)
                question_and_answers.write('"%s", "%s"\n'%(test.question, test.response))

                if not test.answers_regex:
                    if test.response == "":
                        break
                else:
                    for expected_regex in test.answers_regex:
                        # print("test.answers_regex: {}".format(test.answers_regex))
                        regex_type = expected_regex[0]
                        expression = expected_regex[1]
                        match = expression.search(response)
                        if match is not None and regex_type == "+":
                            success = True
                            break
                        elif match is None and regex_type == "-":
                            success = True
                            break

                if success:
                    successes.append(test)
                else:
                    failures.append(test)

        question_and_answers.flush ()
        question_and_answers.close ()

        stop = datetime.datetime.now()
        diff = stop-start
        total_tests = len(successes)+len(failures)

        
        if warnings > 0:
            print("Warnings:  %d" % warnings)
        for failure in failures:
            print("\t%s: [%s] expected [%s], got [%s]" % (failure.category, failure.question, failure.answers_string, failure.response))
            if failure.answers_string is "None" or failure.answers_string is "":
                line = "\t%s: [%s] expected [%s], got [%s]\n" % (failure.category, failure.question, failure.answers_string, failure.response)
                f = open("results/empty.txt", "a")
                f.write(line)
                f.close()
            else:
                line = "\t%s: [%s] expected [%s], got [%s]\n" % (failure.category, failure.question, failure.answers_string, failure.response)
                f = open("results/errors.txt", "a")
                f.write(line)
                f.close()

        for success in successes:
            line = "\t%s: [%s] expected [%s], got [%s]\n" % (success.category, success.question, success.answers_string, success.response)
            f = open("results/successes.txt", "a")
            f.write(line)
            f.close()

        print("Total processing time %f.2 secs"%diff.total_seconds())
        print("Thats approx %f aiml_tests per sec"%(total_tests/diff.total_seconds()))
        print("Successes: %d" % len(successes))
        print("Failures:  %d" % len(failures))

if __name__ == '__main__':

    def run():
        print("Loading, please wait...")
        console_app = TestRunnerBotClient()
        console_app.run()

    run()
