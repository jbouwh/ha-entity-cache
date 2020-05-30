# ha-entitiy-cache
AppDaemon based entity cache application for Home Assistant

## Example config (/conf/appdaemon/apps/apps.yaml)
```yaml
ha-entity-cache:
  module: entitycache
  class: EntityCache
# The cache_file setting is optional and defaults to cache.json in the script current folder
  cache_file: /config/appdaemon/apps/ha-entity-cache/cache.json
  entities:
    input_select.test: option
```

Under `entities` place the entity names followed with the type of the entity that is to cached.
Caching of attributes is _not_ supported with this version, but might be feature in future.
Supported types are:
* `option`: For caching input selects
* `text`: For caching text inputs
* `value`: For caching numeric inputs
* `switch`: for caching on / off controls

## Installation (With AppDaemon add on on Home Assistant) or use HACS (Home Assistant Community store)
Unpack the script files at `/config/appdaemon/`. The active script is 