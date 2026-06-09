import json
import os
import sys

# # # # #
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# # # # #

class action(object):
    def __init__(self, keyword:str, text:str, execute_text:str = "", next_section = None,
                 vars_needed_to_show = [], negative_vars_needed_to_show = [], vars_set_true = [], vars_set_false = []):
        self.keyword = keyword
        self.key_number = -1
        self.text = text
        self.execute_text = execute_text
        self.next_section = next_section
        self.next_section_id = -1
        self.vars_needed_to_show = vars_needed_to_show
        self.negative_vars_needed_to_show = negative_vars_needed_to_show
        self.vars_set_true = vars_set_true
        self.vars_set_false = vars_set_false
    
    def set_key_number(self, key_number:int):
        self.key_number = key_number

    global current_save

    def can_display(self) -> bool:
        for var in self.vars_needed_to_show:
            if not var in current_save or current_save[var] == False:
                return False

        for var in self.negative_vars_needed_to_show:
            if not var in current_save:
                continue
            if current_save[var] == True:
                return False

        return True

    def execute(self, text_input:str) -> bool:
        if text_input.lower() != self.keyword.lower() and text_input != str(self.key_number):
            return False
        
        if self.execute_text != "":
            print("")
            print(self.execute_text)
            print("")
            input("press any key to continue")
        
        ## Variable switch
        for var in self.vars_set_true:
            current_save[var] = True
        
        for var in self.vars_set_false:
            current_save[var] = False

        if self.next_section != None:
            section_switch(self.next_section)
            return True

        return False

class section(object):
    dialogue:list[str]
    actions:list[action]

    def __init__(self):
        self.dialogue = []
        self.actions = []
    
    def add_dialogue(self, text:str):
        self.dialogue.append(text)
    
    def add_action(self, action:action):
        self.actions.append(action)

    def display(self):
        set_current_section(self)

        for d in self.dialogue[:-1]:
            print(d)

            print("")
            input("press any key to continue\n")
            print('\033[F\033[K', end='', flush=True)

        print("")
        print(self.dialogue[-1])
        print("")

        ## Print actions
        id = 1
        for a in range(len(self.actions)):
            if not self.actions[a].can_display():
                continue

            print(id," - ", self.actions[a].text)
            self.actions[a].set_key_number(id)
            id += 1
        print("")

        text_input = input("What will you do?\n")
        while not self.process_input(text_input):
            print('\033[F\033[K', end='', flush=True)
            text_input = input('\r')
    
    def process_input(self, input) -> bool:
        processed:bool = False
        for a in self.actions:
            if a.execute(input): processed = True
        
        return processed

current_section:section = None
last_section:section = None

def set_current_section(section:section):
    global current_section
    current_section = section

def section_switch(new_section:section):
    global current_section
    global last_section
    
    temp = current_section

    clear_screen()
    current_section = new_section
    
    last_section = temp

    global current_selected_slot
    global current_game

    save_game(current_selected_slot, current_game.index(current_section), current_game.index(last_section))

    current_section.display()

def clear_screen():
    cmd = "cls" if os.name == "nt" else "clear"
    os.system(cmd)  

# # # # #

def save_game(slot:int, current_section_id:int , last_section_id:int):
    global current_save

    current_save["current_section"] = current_section_id
    current_save["last_section"] = last_section_id

    with open(resource_path('save'+str(slot)+'.json'), 'w') as f:
        json.dump(current_save, f, indent=4)

def load_new_game(slot:int):
    with open(resource_path('newsave.json')) as n:
        new_save = json.load(n)

    with open(resource_path('save'+str(slot)+'.json'), 'w') as f:
        json.dump(new_save, f, indent=4)
    
    load_game(slot)

def load_game(slot:int):
    with open(resource_path('save'+str(slot)+'.json')) as f:
        save = json.load(f)
    
    loaded_game:list[section] = []

    with open(resource_path('sections.json')) as f:
        game = json.load(f)

    for i in range(len(game)):
        sec = section()
        for d in game[str(i)]["dialogue"]:
            sec.add_dialogue(d)
        loaded_game.append(sec)
    
    for s in range(len(loaded_game)):
        for a in game[str(s)]["actions"]:
            act = action(keyword=a["keyword"], text=a["text"], execute_text=a["execute_text"],
                         next_section=loaded_game[a["next_section_id"]] if a["next_section_id"] >= 0 else None,
                         vars_needed_to_show=a["vars_needed_to_show"], negative_vars_needed_to_show=a["negative_vars_needed_to_show"], vars_set_true=a["vars_set_true"], vars_set_false=a["vars_set_false"])
            loaded_game[s].add_action(act)
    
    clear_screen()

    global current_game
    current_game = loaded_game

    global current_selected_slot
    current_selected_slot = slot

    global current_save
    current_save = save

    global last_section
    last_section = current_game[save["last_section"]]

    current_game[save["current_section"]].display()

    

current_selected_slot = 1
current_game:list[section] = []

## Main Menu
with open(resource_path('mainmenu.json')) as m:
    main_values = json.load(m)

print(main_values["title"])
print("")
if main_values["description"] != "":
    print(main_values["description"])
    print("")
print("1 - New Game")
print("2 - Load Game")
print("")

main_input = input("")
while not main_input in ["1", "2", "new", "load"]:
    print('\033[F\033[K', end='', flush=True)
    main_input = input('\r')
print("")
if main_values["allow_multiple_saves"]:
    if main_input in ["1", "new"]:
        print("Choose the desired save slot for the new game")
    else:
        print("Choose the desired save slot to load")
    print("")
    print("1 - save slot 1")
    print("2 - save slot 2")
    print("3 - save slot 3")
    print("")
    save_input = input("")
    while not save_input in ["1", "2", "3"]:
        print('\033[F\033[K', end='', flush=True)
        save_input = input('\r')
    if main_input in ["1", "new"]:
        load_new_game(int(save_input))
    else:
        load_game(int(save_input))
else:
    if main_input in ["1", "new"]:
        load_new_game(1)
    else:
        load_game(1)

