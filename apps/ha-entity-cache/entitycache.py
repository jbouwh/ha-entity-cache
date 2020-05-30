#! /usr/bin/env python

import appdaemon.plugins.hass.hassapi as hass
import json
import pathlib

# Initialization class for AppDaemon (homeassistant)
class EntityCache(hass.Hass):

    def initialize(self, *args, **kwargs):
        self.log("Entity cache started")
        self.handle = {}
        self.state = {}
        self.log(f"args: {self.args}")
        self.mainpath = pathlib.Path(__file__).parent.absolute()
        self.file = self.args['cache_file'] if 'cache_file' in self.args else f'{self.mainpath}/cache.json'
        if 'entities' in self.args:
            for entity in self.args['entities']:
                self.handle[entity] = self.listen_state(self.callback, entity)
                self.log(f"Cache enabled for entity: {entity}")
        else:
            self.log("No entries found to cache", level='WARNING')
            return
        try:
            with open(self.file, 'r') as self.filehandle:
                self.cachedstate = json.load(self.filehandle)
            self.filehandle.close()
            self.log(f'Read from file: {self.cachedstate}')
            # Recover the state from file
            for entity in self.cachedstate:
                # Todo: replace set_state() with a better compatible: set_option(), set_text(), set_value() turn_on/off
                entity_type = self.args['entities'][entity]
                if entity_type:
                    if entity_type == 'option':
                        self.select_option(entity, self.cachedstate[entity])
                    elif entity_type == 'text':
                        self.set_text(entity, self.cachedstate[entity])
                    elif entity_type == 'value':
                        self.set_value(entity, self.cachedstate[entity])
                    elif entity_type == 'switch':
                        if self.cachedstate[entity] == 'on':
                            self.turn_on(entity)
                        elif self.cachedstate[entity] == 'off':
                            self.turn_on(entity)
                    else:
                        # Use the generic method if everyting else fails
                        self.set_state(entity, state=self.cachedstate[entity])

                self.log(f"State recovered for entity '{entity}': {self.cachedstate[entity]}")            
        except Exception as e:
            self.log(f"Cache file '{self.file}' could not be parsed. THis is no problem if this is the first time this application starts. Error: {e}", level='WARNING')
            raise e

    def terminate(self):
        for entity in self.handle:
            self.cancel_listen_state(self.handle[entity])
            self.log(f"Caching for entity '{entity}' was stopped.")

    def callback(self, entity, attribute, old, new, kwargs):
        self.state[entity] = new
        # Update the state on file
        try:
            with open(self.file, 'w') as self.filehandleout:
                json.dump(self.state, self.filehandleout)
            self.filehandleout.close()
            self.log(f"Cache file updated '{entity}' = '{new}'", level='INFO')
        except Exception as e:
            self.log(f"Cache file '{self.file}' was not updated. Check your configuration.", level='ERROR')
