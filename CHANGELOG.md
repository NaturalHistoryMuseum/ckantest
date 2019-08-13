# Changelog
All notable changes to this project will be documented in this file.

The format is (loosely) based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
_While this project is still in alpha, all the changes are going to be pushed directly to master, so 'unreleased' just means 'untagged'._

### Bugfix 0.1.2
- Unload plugins when resetting config

### Bugfix 0.1.1
- Moved blueprint registration out of `load_plugins` into its own method (`register_blueprints`) in `Configurer` as it's the only part that needs an `app`
- Explicitly add plugins to `config['ckan.plugins']`
- Config first, then create app, then register blueprints

## [0.1.0] - 2019-08-08
_Initial release._

### Added
- Factories:
    - `DataFactory` for generating data and adding it to the datastore
- Models:
    - `TestBase` as a generic base class most tests should be able to inherit from
- Helpers:
    - `Configurer` to manage the config
    - `mocking` has common mocking 



[Unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/olivierlacan/keep-a-changelog/releases/tag/v0.1.0