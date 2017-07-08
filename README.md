# docknv

## Installation

```bash
git clone https://bitbucket.org/sharingcloud/docknv.git
pip install --upgrade -e ./docknv # or sudo
```

## Introduction

**docknv** (for *Docker with environments*) is a wrapper around *Docker* and *Docker Compose* to handle some tasks easily.  

Here are the features:

- **Environment configuration management**: you can define environment configuration files, to easily set values.
- **Templating system**: you can insert your defined environment values in templates all over your volumes files, using a simple templating system.
- **Mixing Compose files**: you can merge classic Docker Compose templates together !
- **Use schemas to isolate**: you can isolate portions of infrastructure to build and run services independently.
- **Freezing**: you have to push your stack to production, with or without Docker Swarm, and you have relative path volumes linked to your containers ? You can freeze everything and automatically prepare freezed images. More importantly, you can reverse the freezing and return to *developer mode*.

## Using docknv

### Project structure

To use **Docknv**, you need to respect the following structure, all contained in a parent folder:

- **envs**: The location of your environment configuration files, ending with `.env.py` (example for *debug*, the filename is `debug.env.py`)
- **images**: The location of your Docker images, one folder per container. You should always use the "building" way (instead of the direct fetching) when including new Docker images in your Compose files, to permit freezing.
- **shared**: The location of your shared volumes, one folder per image is recommended if needed.
- **templates**: The location of your Docker Compose files.
- **config.yml**: The main Docknv configuration file for your project

### Environment configuration management

### Templating system

### Mixing Compose files

### Use schemas to isolate

### Configuration syntax example - config.yml