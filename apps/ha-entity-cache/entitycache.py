#! /usr/bin/env python

import appdaemon.plugins.hass.hassapi as hass
import json
import pathlib

# Initialization test class for AppDaemon (homeassistant)
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
        try:
            with open(self.file, 'r') as self.filehandle:
                self.cachedstate = json.load(self.filehandle)
            self.filehandle.close()
            self.log(f'Read from file: {self.cachedstate}')
            # Recover the state from file
            for entity in self.cachedstate:
                self.set_state(entity, state=self.cachedstate[entity])
                self.log(f"State recovered for entity {entity}: {self.cachedstate[entity]}")            
        except Exception as e:
            self.log(f"Cache file '{self.file}' does not exist. No problem if this is the first time this application starts. Error: {e}", level='WARNING')
            raise e


    def terminate(self):
        for handle in self.handle:
            self.cancel_listen_state(handle)
            self.log("Caching was stopped.")

    def callback(self, entity, attribute, old, new, kwargs):
        self.log(f"Call back for {entity}:")
        self.log(f"Old data: {old}")
        self.log(f"New data: {new}")
        self.state[entity] = new
        # Update the state on file
        try:
            with open(self.file, 'w') as self.filehandleout:
                json.dump(self.state, self.filehandleout)
            self.filehandleout.close()
        except Exception as e:
            self.log(f"Cache file '{self.file}' was not updated. Check your configuration.", level='ERROR')



