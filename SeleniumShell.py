#############################################################################################################################################
__filename__ = "SeleniumShell.py"
__description__ = """Provides functionality of Selenium from within a shell.
For a quick demo, watch https://www.youtube.com/watch?v=0wdqovuE3vs
"""
__author__ = "Anand Iyer"
__copyright__ = "Copyright 2017-18, Anand Iyer"
__credits__ = ["Anand Iyer", "??"]
__version__ = "1.0"
__maintainer__ = "Anand Iyer"
__email__ = "ananddotiyer@gmail.com"
__status__ = "In progress" #Upgrade to complete later.
#############################################################################################################################################

from cmd import Cmd
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import os, sys, traceback
import pyperclip
from selenium.common.exceptions import *
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Selenium (Cmd, object):
    args = ''

    def __init__(self):
        Cmd.__init__(self)
        self.prompt = "=>> "
        self.intro  = "Welcome to Selenium shell...\nIMPORTANT: Before you start, please ensure config.txt has the correct settings\n(Copyright 2017-18, Anand Iyer)"
        self.file = None
        self.config = {}
        self.elements = None
        self.element = None
        self.attribute = None
        self.get = None
        
        self.get_config (os.path.realpath(__file__) + "\\config.txt")
        self.config_backup = self.config.copy ()
        
    #Selenium methods      
    def do_browse(self, args):
        """
        Navigates to the given URL in the browser.
        Automatically prefixes "http://" to the given web-page.
        Defaults to homepage set in config.py
        """
        args = self.process_args (args)
    
        try:
            if len(args) == 0:
                url = self.config["homepage"]
            else:
                url = args
            
            if not url.startswith ("http"): #or https
                url = "http://" + url
                
            if self.config["browser"] == None or self.config["browser"] == "firefox":
                self.config["browser"] = webdriver.Firefox(executable_path=self.config["geckodriver_path"])
            if self.config["browser"] == "chrome":
                self.config["browser"] = webdriver.Chrome (self.config["chromedriver_path"])
            
            self.config["browser"].get(url)
            self.config["browser"].maximize_window ()
            self.config["browser"].implicitly_wait(0)
        except:
            self.handle_exception ()
            
    def do_find (self, args):
        """
        Find matching elements from the DOM
        If 'by' is set to 'title', use @title in an appropriate xpath.
        If 'by' is set to 'text', use text() method in xpath', or auto-updates to 'partial_text' (which uses "contains" method in xpath)
        """
        args = self.process_args (args)
        
        self.element = None
        self.elements = None
        
        countLoop = 0
        elementFound = False

        if self.config["by"] != None:
            #try 4 times by default, before giving up.  Or self.config["tries"].
            while countLoop <= int (self.config["tries"]) and not elementFound:
                try:
                    if self.config["by"] == 'title':
                        self.locator = ("text", "//*[@title=\"" + args + "\"]")
                        elementFound = self.find ("xpath",  self.locator[1])
                    elif self.config["by"] == 'text':
                        try:
                            self.locator = ("text", "//*[text()=\"" + args + "\"]")
                            elementFound = self.find ("xpath",  self.locator[1])
                        except:
                            self.locator = ("partial_text", "//*[contains (text(),\"" + args + "\")]")
                            elementFound = self.find ("xpath",  self.locator[1])
                    else:
                        self.locator = (self.config["by"], args)
                        elementFound = self.find (self.config["by"],  args)
                except:
                    self.handle_exception ()

                sleep (1)
                countLoop += 1
        elif (self.config["by"] != 'partial_text' and self.config["by"] != 'text'):
            while countLoop <= int (self.config["tries"]) and not elementFound:
                    print "(%d) Trying all available locators [unable to locate element using 'by']" %(countLoop)
                    by_list = ["id", "name", "xpath", "partial_link_text", "link_text", "tag_name", "class_name", "css_selector"]
                    import collections
                    all_locators = collections.OrderedDict ()
                    for by in by_list:
                        all_locators[by] = args

                    elementFound = self.find_each (all_locators)
                    
                    sleep (1)
                    countLoop += 1

        if elementFound:
            print self.locator,
            if not self.config["actions"]:
                print " found %s elements" %(len(self.elements)),

            print
        else:
            print '-'*60
            print 'Unable to locate web-element using any of the available locators!'
            print '-'*60            
    
    def do_click (self, args):
        """Clicks on the specified web-element"""
        try:
            if not self.config["actions"]:
                self.locate_element ()
                self.element.click ()
        except:
            self.handle_exception ()
            

    def do_send_keys (self, args):
        """Send keys to the specified web-element"""
        args = self.process_args (args)
        
        try:
            if not self.config["actions"]:
                self.locate_element ()
                self.element.send_keys(args)
        except:
            self.handle_exception ()

    def do_close (self, args):
        """Closes the browser"""
        try:
            self.quit_browser ()
        except:
            self.handle_exception ()

    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."

        try:
            self.quit_browser ()
            raise SystemExit
        except:
            self.handle_exception ()

    #infra methods
    def do_set (self, args):
        """
        Supports the following options.  Corresponding values passed after '='.
        1.browser: used to indicate which browser to use during script runs.  Available options=Firefox, Chrome
        2.by: used for locator-based web-element search.  Available options=title, text, partial_text, id, name, xpath, partial_link_text, tag_name, class_name, css_selector
        3.until: used for waiting until expected conditions is met.  Available options=click, present, visible, invisible, text, text_present, text_present_locator, selection_state, located_selection_state
        4.tries:used to indicate number of times to repeat find_element logic in loops.
        5.index:used to indicate the index of element, returned by the last find operation.
        6.trace: used to set to 'on' and 'off'.
        
        Value can be a return value from a eval (expression)
        """
        args = str (args).split ('=')
        
        key = self.process_args (args[0])
        value = self.process_args (args[1].lower())
        
        try:
            if value.startswith ("eval"):
                value = eval (value)
                if type (value) == str:
                    value = value.lower ()
            
            self.config[key] = value

            if key == "index":
                self.locate_element ()
                self.highlight_element()
        except:
            self.handle_exception ()
        
    def do_reset (self, args):
        """Reset a previous setting"""""
        args = self.process_args (args)

        if args == "all":
            for key in self.config_backup.keys():
                #if the browser already has an associated session,don't reset.  Reset all else.
                if not (key == "browser" and type (self.config[key] == str)):
                    self.config[key] = self.config_backup[key]
        else:
            #if the browser already has an associated session,don't reset
            if not (args == "browser" and type (self.config[args] == str)):
                self.config[args] = self.config_backup[args]

    def do_getattr (self, args):
        """
        Gets the attribute of the most recent web-element.
        Available options=tag_name, type, text, innerHTML, outerHTML, size, location, parent, id, name, page_title
        """
        args = self.process_args (args)

        try:
            self.locate_element ()
            if args == "page_title":
                self.locator = ("browser", "browser") #so that 'equals' and 'contains' gives output, consistent with other locators.
                self.get = (args, getattr (self.config["browser"], "title"))
                self.attribute = args
            else:
                self.get = (args, getattr (self, "element." + args))
                self.attribute = args
            print self.get
        except:
            try:
                if self.element:
                    self.get = (args, self.element.get_attribute (args))
                    self.attribute = args
                    print self.get
            except:
                self.handle_exception ()

        #copy xpath to clipboard
        xpath = "//*"
        attribs = {'id':'@id', 'name':'@name', 'text':'text()'}
        for attrib in attribs.keys():
            try:
                element_attrib = self.element.get_attribute (attrib)
                if not (element_attrib == "" or element_attrib == "None"):
                    xpath += "[%s='%s']" %(attribs[attrib], element_attrib)
            except:
                pass
        
        pyperclip.copy (xpath)
                        
    def do_equals (self, args):
        "Verifies if the given value is same the most recent get_attribute"
        args = self.process_args (args)

        try:
            if args == self.get[1]:
                print "True\n('%s', '%s', '%s')" %(self.locator[1], self.attribute, args)
            else:
                print "False\n('%s', '%s', '%s')" %(self.locator[1], self.attribute, args)
        except:
            self.handle_exception()
            
    def do_contains (self, args):
        "Verifies if the most recent get_attribute contains (substring) given value"
        args = self.process_args (args)
        
        try:
            if args in self.get[1]:
                print "True\n('%s', '%s', '%s')" %(self.locator[1], self.attribute, args)
            else:
                print "False\n('%s', '%s', '%s')" %(self.locator[1], self.attribute, args)
        except:
            self.handle_exception()
            
    def do_what (self, args):
        """Outputs the present value of a variable"""
        args = self.process_args (args)
        
        try:
            print getattr (self, "config")['%s' %(args)]
        except:
            self.handle_exception ()

    def do_eval (self, args):
        """Evaluates the given string as a Python statement"""
        args = self.process_args (args)
        
        try:
            self.locate_element ()
            print eval (args)
        except:
            self.handle_exception ()

    def do_start(self, args):
        'Use it for recording, and creating actionchains'
        args = self.process_args (args)
        
        if args == '':
            args = 'record'
        
        if args == 'record' and not self.config["actions"]:
            self.file = open(args + ".txt", 'w')
        elif args == 'actions':
            self.config["actions"] = True
            self.actionsList = []
            self.actions_elements = []
            
    def do_playback(self, args):
        'Playback commands from a recorded sequence'
        args = self.process_args (args)
        
        if args == '':
            args = 'record.txt'
        self.do_stop (args)
        try:
            with open(args) as f:
                self.cmdqueue.extend(f.read().splitlines())
        except:
            print '-'*60
            print 'Specified file not found!'
            print '-'*60            

    def do_stop(self, args):
        'Use it to denote end of recording, and actionchains'
        args = self.process_args (args)
        
        if args == '':
            args = 'record'

        if self.file and args == 'record' and not self.config["actions"]:
            self.file.close()
            self.file = None
        elif args == 'actions':
            self.config["actions"] = False
            try:
                action_chains = ActionChains(self.config["browser"])
                
                #constructing the actions sequence
                mod_actions = []
                index_action_elements = 0
                for action in self.actionsList:
                    mod_actions.append (self.build_function (action, "self.actions_elements[%d]" %(index_action_elements)))
                    index_action_elements += 1
                
                action_chains_string = 'action_chains.' + '.'.join (mod_actions) + '.perform()'
                eval (action_chains_string)
                self.actions_elements = []
            except:
                self.handle_exception ()
            
            self.actionsList = []

    #internal methods
    def quit_browser (self):
        self.config["browser"].quit ()
        self.config["browser"] = None
    
    def find (self, by, locator, *kwargs):
        try:
            self.locator = (by, locator)
            
            if by == "link_text":
                by = "partial_link_text"

            if self.config["actions"]:
                self.actions_elements.append (getattr (self.config["browser"], "find_element_by_" + by) (locator))
            else:
                self.elements = getattr (self.config["browser"], "find_elements_by_" + by) (locator) #this won't raise an exception, but return an empty list
                if len (self.elements) == 0:
                    raise
                
            return self.wait_until (by, locator, *kwargs) #elementFound
        except:
            raise
            return False

    def find_each (self, all_locators):
        by_list = all_locators.keys()
        by = by_list[0]
        iter_by = iter (by_list[1:])
        try:
            elementFound = self.find (by, all_locators[by])
            if elementFound:
                return elementFound
        except:
            if len (all_locators) == 1:
                return False
            else:
                iter_by.next()
                del all_locators[by]
                return self.find_each (all_locators)

    def wait_until (self, by, path, *args):
        """Wait until expected condition is met.  Used internal to find method"""
        try:
            wait = WebDriverWait(self.config["browser"], 10)
            if self.config["until"] == "click":
                _ = wait.until(EC.element_to_be_clickable((by, path)))
            if self.config["until"] == "present":
                _ = wait.until(EC.presence_of_element_located((by, path)))
            if self.config["until"] == "visible":
                _ = wait.until(EC.visibility_of_element_located((by, path)))
            if self.config["until"] == "invisible":
                _ = wait.until(EC.invisibility_of_element_located((by, path)))
            if self.config["until"] == "text_present":
                _ = wait.until(EC.text_to_be_present_in_element((by, path, kwargs))) #_text
            if self.config["until"] == "text_present_locator":
                _ = wait.until(EC.text_to_be_present_in_element_value((by, path, kwargs))) #_text
            if self.config["until"] == "selection_state":
                _ = wait.until(EC.element_selection_state_to_be((by, path)))
            if self.config["until"] == "located_selection_state":
                _ = wait.until(EC.element_located_selection_state_to_be((by, path, kwargs))) #is_selected
            return True
        except:
            return False

    def highlight_element (self):
        with open ("get_element_border.js") as script_get_element_border:
            SCRIPT_GET_ELEMENT_BORDER = ''.join (script_get_element_border.readlines ())

        self.unhighlight_last()
        
        #remember last element to highlight
        self.last_element = self.element
        self.last_border = self.config["browser"].execute_script (SCRIPT_GET_ELEMENT_BORDER, self.element)
        #self.config["browser"].execute_script("arguments[0].style.border='2px solid red'", self.element)

    def unhighlight_last (self):
        with open ("unhighlight_last.js") as script_unhighlight_last:
            SCRIPT_UNHIGHLIGHT_LAST = ''.join (script_unhighlight_last.readlines ())

        try:
            self.config["browser"].execute_script (SCRIPT_UNHIGHLIGHT_LAST, self.last_element, self.last_border);
        except:
            pass

    def handle_exception (self):
        if self.config["trace"] == 'on':
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60            

    def get_config (self, filepath):
        #reading config file
        fp = open ("config.txt")
        for line in fp:
            line = self.process_args (line)
            try:
                if '=' in line:
                    items = line.split ('=')
                    key = self.process_args (items[0])
                    value = self.process_args (items[1])
                    self.config[key] = self.get_value (value)
            except:
                pass
        fp.close ()
    
    def get_value (self, arg):
        if arg == "None":
            return None
        elif arg == "True":
            return True
        elif arg == "False":
            return False
        else: #integer or string
            try:
                return int (arg)
            except ValueError:
                return str (arg)
    
    def locate_element (self):
        self.element = self.elements[int (self.config["index"]) - 1]
    
    def build_function (self, action, element):
        pre = re.findall(r'([\w\.]+|".*?")', action) #break into multiple pieces around spaces, unless they're inside double quotes.  However treat Keys.ENTER as a single piece.
        
        return (pre[0] + "(" + ','.join (pre[1:]).strip ("[]").replace ("it", element) + ")")
    
    def process_args (self, args):
        return args.strip(' ').strip ('"\'').strip ('\n')
    
    #cmd.py - redefined, overridden methods
    def onecmd (self, line):
        supported_commands = ['browse', 'find', 'click', 'send_keys', 'close', 'quit', 'set', 'reset',
                              'getattr', 'equals', 'contains', 'eval',
                              'what', 'start', 'playback', 'stop', 'help']

        if self.file and line.startswith ('#'): #lines starting with # are comments; don't process them.
            self.file.write (line + '\n')

        cmd, arg, line = self.parseline(line)
        
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else: #valid command
            cmd = cmd.lower ()
            #record if these are actions, even if these aren't supported commands
            if self.file and not (cmd == 'stop' and arg == 'record'):
                self.file.write (line + '\n')

            if cmd not in supported_commands:
                return
            else:
                try:
                    func = getattr(self, 'do_' + cmd)
                except AttributeError:
                    return self.default(line)

                return func(arg)
    
    def cmdloop(self, intro=None):
        print(self.intro)
        while True:
            try:
                super(Selenium, self).cmdloop(intro="")
                self.postloop()
                break
            except KeyboardInterrupt:
                print("^C")

    def default (self, line):
        pass
    
    def precmd(self, line):
        return line
    
    def postcmd(self, stop, line):
        super(Selenium, self).postcmd (stop, "")
        allowed = False
        allowed_commands = ['click', 'send_keys', 'key_down', 'key_up', 'move_to_element']
        for each in allowed_commands:
            if line.startswith (each):
                allowed = True
                break

        if self.config["actions"] and (allowed):
            self.actionsList.append (line)
        sleep (1)

    def emptyline (self):
        pass
    
if __name__ == '__main__':
    prompt = Selenium ()
    prompt.prompt = '> '
    prompt.cmdloop()