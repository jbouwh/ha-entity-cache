# ha-entity-cache
![ha-entity-cache](https://github.com/jbouwh/ha-entity-cache/workflows/ha-entity-cache/badge.svg)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

AppDaemon based entity cache application for Home Assistant.

*IMPORTANT NOTE. Native Home Assistant already caches content. You will not need this add-on if you did not specify an initial value in your Home Assistant configuration!*

## Example config (/conf/appdaemon/apps/apps.yaml)
```yaml
ha-entity-cache:
  module: entitycache
  class: EntityCache
# The cache_file setting is optional and defaults to cache.json in the script current folder
  cache_file: /config/appdaemon/apps/ha-entity-cache/cache.json
  entities:
    - input_select.test
    - climate.rpi_cooling_fan_controller
  input_select.test:
    state_cache_type: option
  climate.rpi_cooling_fan_controller: 
    attributes:
      - temperature
```

Place the entities for caching as a list under `entities:`.

For each entity a _entity_name_: section must exist.

### State caching
Define the key `state_cache_type:` under the _{entity name}_ section.

Supported `state_cache_type` options are:
* `option`: For caching input selects
* `text`: For caching text inputs
* `value`: For caching numeric inputs
* `switch`: for caching on / off controls

### Attribute caching
Define the key `attributes:` under the _{entity name}_ section.
The list of attribute names is a list under this key

## Installation (With AppDaemon add on on Home Assistant) or use HACS (Home Assistant Community store)
Unpack the script files at `/config/appdaemon/`. The active script is then located at `/config/appdaemon//apps/ha-entity-cache/entitycache.py'

After startup, ha-entity-cache listens to updates of the values. That is the moment values are cached and restored after a restart of Home Assistant.
At restore the type is checked. If a not valid type is entered, the value might not be restored, or not correct.
