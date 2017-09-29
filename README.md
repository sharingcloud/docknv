# docknv 3.7.2

**DOCUMENTATION IN WIP**

## Installation

```bash
git clone https://bitbucket.org/sharingcloud/docknv.git
pip install --upgrade -e ./docknv # or sudo
```

## Introduction

**docknv** (for *Docker with environments*) is a wrapper around *Docker*, *Docker Compose* and *Docker Swarm*.

Here are the features:

- **Environment configuration management**: you can define environment configuration files, to easily set and use values.
- **Templating system**: you can insert your defined environment values in templates all over your volumes files, using the powerful Jinja2 template engine!
- **Mixing Compose files**: you can easily merge classic Docker Compose templates together!
- **Use schemas and namespaces to isolate**: you can isolate portions of infrastructure to build and run services independently.
- **Concurrent executions**: on a single host, and from the same entry point, you can deploy multiple schemas in different namespaces.
- **Custom commands**: you can extend the docknv command system to include your own custom commands and execute any action within docknv!

## About docknv

### Project structure

To use **Docknv**, you need to respect the following structure, all contained in a root folder:

- **commands**: The location of your custom docknv commands. *(optional)*
- **composefiles**: The location of your Docker Compose files.
- **data**: Your project data, organized in three different folders:
    - **files**: Static files and Jinja2 templates imported via volumes should be stored here, with one folder per container
    - **standard**: Here you can put private files to be imported
- **envs**: The location of your environment configuration files, ending with `.env.py` (example for *debug*, the filename is `debug.env.py`). By default, there is always a `default.env.py`.
- **images**: The location of your Docker images, one folder per container. You should always use the "building" way (instead of the direct fetching) when including new Docker images in your Compose files.
- **config.yml**: The main Docknv configuration file for your project.

### Environment configuration management

TODO

### Templating system

TODO

### Mixing Compose files

TODO

### Use schemas and namespaces to isolate

TODO

## Using docknv

You can use docknv on a project from scratch by letting it automatically create your project tree, or use it on an already *docknv-configured* project.

### Create a new project

You can use the `scaffold` subparser to create a new project.
