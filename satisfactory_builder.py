# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 15:27:01 2021

@author: joshj
"""

import pandas as pd
from math import ceil

'''
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class InputWindow(GridLayout):

    def __init__(self, **kwargs):
        super(InputWindow, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='Material'))
        self.material = TextInput(multiline=False)
        self.add_widget(self.material)
        self.add_widget(Label(text='Production/min'))
        self.rate = TextInput(multiline=False)
        self.add_widget(self.rate)


class MyApp(App):

    def build(self):
        return InputWindow()
'''

def round_special(x, base=2):
    return base * ceil(x/base)

def find_factor(wanted_rate, rate_per_machine, overclock=False):
    N = 0
    p = 99999
    Y = (250 if overclock else 100)
    while p > Y:
        N += 1
        p = 100 * wanted_rate / (N * rate_per_machine)
    return (ceil(p), N)

def initialize_results():
    global results
    results = {'Total Power Usage':0, 
               'Inputs':{}, 
               'Machines':{
                   'Smelter':0,
                   'Foundry':0,
                   'Constructor':0,
                   'Assembler':0,
                   'Manufacturer':0,
                   'Refinery':0}}

def update_results(power, inputs, machine, num_machines):
    global results
    results['Total Power Usage'] += power
    results['Machines'][machine] += num_machines
    for m,r in inputs.items():
        if m in results['Inputs'].keys():
            results['Inputs'][m] += r
        else:
            results['Inputs'][m] = r

def print_step(rate, material, machine, num_machines, clock_speed, inputs, power):
    print(f'{rate} {material} per minute.')
    print(f'   Machines: {num_machines} {machine}s')
    print(f'   Clock Speed: {clock_speed}%')
    print('   Inputs:')
    for m,r in inputs.items():
        print(f'      {m} ({r}/min)')
    print(f'   Power usage for this step: {power} MW')
    print('')    

def make(material=None, rate=0, overclock=False):
    global results
    
    recipe = recipes.loc[material]

    if rate % 1 > 0:
        rate = ceil(rate)
    
    (clock_speed, num_machines) = find_factor(rate, 
                                              recipe['Output Rate'], 
                                              overclock=overclock)
    
    inputs = {}
    for i in range(1, 5):
        if not(recipe[f'Input {i} Name'] == 'None'):
            inputs[recipe[f'Input {i} Name']] = round_special(num_machines * \
                (clock_speed/100) * recipe[f'Input {i} Rate'])
    
    p = power.loc[recipe['Machine'], 'Power']
    total_power = round(num_machines * p * (clock_speed/100)**1.6, ndigits=3)
    
    for m,r in inputs.items():
        if m in recipes.index:
            make(material=m, rate=r, overclock=overclock)
            
    update_results(total_power, inputs, recipe['Machine'], num_machines)

    print_step(rate, material, recipe['Machine'], num_machines, clock_speed,
               inputs, total_power)
    
def print_results():
    global results
    results['Total Power Usage']=round(results['Total Power Usage'], ndigits=3)
    print('Totals:')
    for k,v in results.items():
        if isinstance(v, dict):
            print(f'   {k}:')
            for c,d in v.items():
                print(f'      {c} = {d}')
        else:
            print(f'   {k} = {v}')
            
def build(material, rate, overclock=False):
    global recipes
    global power
    recipes = pd.read_excel('SatisfactoryRecipes.xlsx', 
                            sheet_name='Recipes', 
                            index_col='NAME')
    
    power = pd.read_excel('SatisfactoryRecipes.xlsx', 
                          sheet_name='Power Usage', 
                          index_col='Machine')
    initialize_results()
    make(material=material, rate=rate, overclock=overclock)
    print_results()
    
    
if __name__=='__main__':
    #build("Turbo Motor", 2)
    pass

    