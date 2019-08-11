# Changelog

## 5.3

- Support config hot-swap in service and custom commands

## 4.2.1

- Handle empty ports in composefiles.

## 4.2

- #1: Moving user configuration inside of project directory
- #2: Manage docknv project inside of another folder
- #3: Refactor project_generate_compose
- #4: Force a unique config name in each project
- #5: Better handling of environment variable inheritance

## 4.1

- Removing `registry` command, tagging system added.

## 4.0

- YAML configuration files instead of Python files
- Merging `schema` and `config` commands.
- More tests and fixes.

## 3.7.4

- Python 3 and Windows support OK.
- Commands arguments cleanup.

## 3.7.3

- Python 3 support on its way!

## 3.7.0

- Context sensitive commands!
  - Commands are configurable using the main `config.yml` file in the `commands` key.

## 3.6.0

- Environment import system!
  - You can now import environments using the following snippet.
  - Example for **base-default**: `# -*- import: base-default -*-`
