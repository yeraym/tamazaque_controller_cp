

class Config:
    def __init__(self, myconfig):
        self.data = myconfig
        self.cur_state = self.data['state']
        self.cur_page = self.cur_state['page']
        self.cur_buttons = self.data['pages'][self.cur_page]['buttons']
        self.cur_expressions = self.data['pages'][self.cur_page]['expression']

    def update(self):
        self.cur_state = self.data['state']
        self.cur_page = self.cur_state['page']
        self.cur_buttons = self.data['pages'][self.cur_page]['buttons']
        self.cur_expressions = self.data['pages'][self.cur_page]['expression']

    def get_button(self, button_name):
        return self.cur_buttons[button_name]

    def get_button_action(self, button_name, event):
        b = self.get_button(button_name)
        if event in b.keys():
            return b[event]

    def get_button_state(self, button_name):
        return self.cur_state[self.cur_page]['buttons'][button_name]['state']

    def get_button_state_action(self, button_name):
        bstate = self.get_button_state(button_name)
        baction = self.get_button_action(button_name, 'state_press')
        if bstate in baction:
            return baction[bstate]

    def set_button_state(self, button_name, state):
        self.cur_state[self.cur_page]['buttons'][button_name]['state'] = state

    def get_page_state(self):
        return self.cur_state[self.cur_page]['page_state']

    def get_button_page_state_action(self, button_name):
        pstate = self.get_page_state()
        baction = self.get_button_action(button_name, 'page_state_press')
        if pstate in baction:
            return baction[pstate]

    def set_page_state(self, state):
        self.cur_state[self.cur_page]['page_state'] = state

    def change_page(self,page):
        self.data['state']['page'] = page
        self.update()

    def control_action(self, control_action):
        if control_action['type'] == 'changepage':
            self.change_page(control_action['value'])

    def page_up(self):
        page_names = list(self.data['pages'].keys())
        pos_next_page = page_names.index(self.data['state']['page'])+1
        if pos_next_page > len(page_names)-1:
            pos_next_page = 0
        self.change_page(page_names[pos_next_page])

    def page_down(self):
        page_names = list(self.data['pages'].keys())
        pos_next_page = page_names.index(self.data['state']['page'])-1
        if pos_next_page < 0:
            pos_next_page = len(page_names)-1
        self.change_page(page_names[pos_next_page])

    def get_expression(self, exp_name):
        if exp_name in self.cur_expressions.keys():
            return self.cur_expressions[exp_name]
        else:
            return None

    def get_expression_action(self, exp_name, event):
        e = self.get_expression(exp_name)
        if e:
            if event in e.keys():
                return e[event]