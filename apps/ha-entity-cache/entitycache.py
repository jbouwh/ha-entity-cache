#! /usr/bin/env python

import appdaemon.plugins.hass.hassapi as hass
import json
import pathlib


# Initialization class for AppDaemon (homeassistant)
class EntityCache(hass.Hass):

    def initialize(self, *args, **kwargs):
        self.log("Entity cache started")
        self.callback = {}
        self.state = {
            'states': {},
            'attributes': {}
            }
        self.log(f"args: {self.args}")

        self.mainpath = pathlib.Path(__file__).parent.absolute()
        self.file = self.args['cache_file'] if 'cache_file' in self.args else f'{self.mainpath}/cache.json'

        # Process attributes
        if 'entities' in self.args:
            for entity in self.args['entities']:
                self._process_entity_config(entity)
        else:
            self.log("No entries or attributes to cache found in config!", level='WARNING')
            return

        # Try to read the content from file
        try:
            with open(self.file, 'r') as self.filehandle:
                self.cachedstate = json.load(self.filehandle)
            self.filehandle.close()
            self.log(f'Read from file: {self.cachedstate}')

        except Exception as e:
            # Start with empty cache
            self.cachedstate = {}
            self.log(f"Cache file '{self.file}' could not be parsed. This is normal if this "
                     f"is the first time this application starts. Error: {e}", level='WARNING')

        # Recover the states from file
        # self.cachedstate['states'][entitiy] = state
        # self.cachedstate['attributes'][entity][attribute] = attribute_state
        if self.cachedstate:
            for entity in self.cachedstate['states']:
                # Recover entity state
                self._recover_entity_state(entity)
            for entity in self.cachedstate['attributes']:
                # Recover attribute state
                self._recover_attribute_state(entity)

    def _process_entity_config(self, entity):
        # Set state recover call back functions for each state type
        state_recover_functions = {
            'option': self.select_option,
            'text': self.set_textvalue,
            'value': self.set_value,
            'switch': self._turn_on_off
            }
        self.callback[entity] = {}
        # call back handles:
        # main state: self.callback[entity]['callback_handle']
        # attributes: self.callback[entity]['attribute_callback_handle'][attribute]
        # Process state cache entities
        if 'state_cache_type' in self.args[entity]:
            if self.args[entity]['state_cache_type'] in state_recover_functions:
                self.callback[entity]['state_recover_function'] = \
                    state_recover_functions[self.args[entity]['state_cache_type']]
                self.callback[entity]['callback_handle'] = self.listen_state(self.state_callback, entity)
                self.log(f"Cache enabled for state entity: {entity}")
        # Process attributes
        if 'attributes' in self.args[entity]:
            self.callback[entity]['attribute_callback_handle'] = {}
            for attribute in self.args[entity]['attributes']:
                self.callback[entity]['attribute_callback_handle'][attribute] = \
                    self.listen_state(self.state_callback, entity, attribute=attribute)
                self.log(f"Cache enabled for attribute '{attribute}' of entity: {entity}")

    def _recover_entity_state(self, entity):
        if 'callback_handle' in self.callback[entity]:
            # Recover state: self.callback[entity]['state_recover_function'] holds the correct set_state function
            self.callback[entity]['state_recover_function'](entity, self.cachedstate['states'][entity])
            self.log(f"State recovered for entity '{entity}': {self.cachedstate['states'][entity]}")
        else:
            self.log(f"Ignoring previous state for entity '{entity}': {self.cachedstate['states'][entity]}")

    def _recover_attribute_state(self, entity):
        entity_state = self.get_state(entity, attribute="all")
        state_updated = False
        for attribute in self.cachedstate['attributes'][entity]:
            if attribute in self.callback[entity]['attribute_callback_handle']:
                # Get complete attribute state befor updating the attribute
                entity_state['attributes'][attribute] = self.cachedstate['attributes'][entity][attribute]
                state_updated = True
                self.log(f"State recovered for attribute '{attribute}' of entity '{entity}': "
                         f"{self.cachedstate['attributes'][entity][attribute]}")
            else:
                self.log(f"Ignoring previous state for attribute '{attribute}' of entity '{entity}': "
                         f"{self.cachedstate['attributes'][entity][attribute]}")
        # Update all recovered attributes using one call
        if state_updated:
            self.set_state(entity, state=entity_state['state'], attributes=entity_state['attributes'])

    def _turn_on_off(self, entity, state):
        state_on = ['on', 'ON', 'On', 'true', 'TRUE', 'True', '1']
        if state in state_on:
            self.turn_on(entity)
        else:
            self.turn_off(entity)

    def terminate(self):
        # close listen_state handles
        for entity in self.callback:
            # main state: self.callback[entity]['callback_handle']
            if 'callback_handle' in self.callback[entity]:
                self.cancel_listen_state(self.callback[entity]['callback_handle'])
                self.log(f"Caching for entity '{entity}' was stopped.")
            # attributes: self.callback[entity]['attribute_callback_handle'][attribute]
            if 'attribute_callback_handle' in self.callback[entity]:
                for attribute in self.callback[entity]['attribute_callback_handle']:
                    self.cancel_listen_state(self.callback[entity]['attribute_callback_handle'][attribute])
                    self.log(f"Caching of attribute '{attribute}' for entity '{entity}' was stopped.")

    def state_callback(self, entity, attribute, old, new, kwargs):
        # With state updates attribute is None
        if attribute == 'state':
            # Store the new value in the state cache
            self.state['states'][entity] = new
        else:
            # Initialize attribute cache for entity if it does not exist
            if entity not in self.state['attributes']:
                self.state['attributes'][entity] = {}
            # Store the new value in the attribute cache
            self.state['attributes'][entity][attribute] = new

        # Flush the cache to file
        try:
            with open(self.file, 'w') as self.filehandleout:
                json.dump(self.state, self.filehandleout)
            self.filehandleout.close()
            self.log(f"Cache file updated '{entity}' = '{new}'", level='INFO')
        except Exception as e:
            self.log(f"Cache file '{self.file}' was not updated. Check your configuration. Error: {e}", level='ERROR')
