# docknv

## Installation

```bash
git clone https://bitbucket.org/sharingcloud/docknv.git
pip install -e ./docknv # or sudo
```

## Introduction

**docknv** (for *Docker and eNVironments*) is a wrapper around *Docker* and *Docker Compose* to handle some tasks easily.  

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

You can specify variables in an environment configuration file, which is a Python file.  
The file extension is `*.env.py`, and they are located in the **/envs** folder.

Since they are Python files, you can perform calculations and use Python libraries to set your variables.

*Example: test (test.env.py)*

```python
MAVAR_1 = "hello"
MAVAR_2 = MAVAR_1 + " world"

HELLO = "wat"
MAVAR_2 += " " + HELLO

MY_PORT = 6000

# ...
```

Once you defined your environment configuration file, you can use it in the templating process, using the `docknv env use <env_name>` command.

### Templating system

Sometimes you need to easily configure some files in your local mounted volumes, for example in the *development* process.  

**docknv** includes a simple templating system, that seek every files ending in `.tpl` in the **/shared** folder, and try to resolve environment variables (defined in the environment configuration files), by rendering the file in place, without the `.tpl` extension.  

Il will seek environment variables in the form `${my_var}`.

*Example: helo.py.tpl (Python file)*

```python
def hello():
  print("Hello ${GLOBAL_NAME}")
```

*Rendering: helo.py (GLOBAL_NAME="world")*

```python
def hello():
  print("Hello world")
```

You need to define an environment configuration file, and use `docknv env use <env_name>`.  
If you have defined a `debug` environment configuration file, you need to type: `docknv env use debug`, that will automatically create a `.env` file in your project folder and render the template files stored in **/shared**.

### Mixing Compose files

If you have multiple Compose sources, or if you want to split your Compose configuration, you can use multiple Compose files, each defined in the same **version**.

Just store them in the **/templates** folder and register them in the *templates* section of the **config.yml** file.

*Example: Compose file n°1 (one.yml)*

```
version: '2'

volumes:
  v1:

services:
  s1:
    # ...
  s2:
    # ...

networks:
  net:
```

*Example: Compose file n°2 (two.yml)*

```
version: '2'

volumes:
  v2:

services:
  t1:
    # ...

networks:
  net:
```

*Example: Merge of "one" and "two"*

```
version: '2'

volumes:
  v1:
  v2:

services:
  s1:
  s2:
  t1:

networks:
  net:
```

Here is the format in the **config.yml** file:

```
project_name: "myproject"

templates:
  - ./templates/one.yml
  - ./templates/two.yml

# ... Schemas section ...
```

To render the merged Compose file, use the `docknv schema generate` command.

### Use schemas to isolate

You may want to isolate parts of your infrastructure, and execute tests or develop using only a subset of your containers: enter **schemas**.  

You define schemas in the **config.yml** file, where you specify the required *volumes*, *services* and *networks* values.  
If you want to include schemas containing others, you just have to use the *includes* property.

*Example:*

```
# ... Project name...

# ... Templates section ...

schemas:
  base:
    volumes:
      - v1
    services:
      - s1
      - s2
    networks:
      - net

  plugin:
    services:
      - plugin1
    networks:
      - net

  full:
    includes:
      - base
      - plugin
```

When you defined schemas, you can generate the Compose file, but first, you need to select the "current" schema.
For example considering the schema *base*:
  - `docknv schema use base`
  - `docknv schema generate`

To list defined schemas, use `docknv schema list`.

Once you generated your Compose file, you can build the needed containers using `docknv schema build`.

### Freezing

Last step before production, you may need to quickly export your volumes inside of your respective containers. That is exactly what the *freezing* process do:

- Check for relative path volumes linked to your containers and copy them in an **exported** folder in the right image in the **/images** folder.
- Edit the respective Docker files (that is why the "building" way is recommended instead of the quick pulling way by specifying a `build` property for each container in your Compose files)
- Removing the volume entries from the current Docker Compose file (`.docker-compose.yml`)

That's it. So here is the workflow if you want to push your stack in freeze mode, using schema `base`:

```bash
  # You may want to use another env file
  docknv env use preprod

  # Select your schema
  docknv schema use base

  # Generate compose
  docknv schema generate

  # Freeze everything and rebuild
  docknv schema export --build

  # Start !
  docknv compose up
```

You can reverse the operation and remove the modifications of the respective Dockerfiles and recreate a Compose file using the `docknv schema export-clean` command.

### Configuration syntax example - config.yml

Here is a **config.yml** example.

```
project_name: myprojectname

templates:
  - ./template/tpl1.yml
  - ./template/tpl2.yml
  # ...

schemas:
  one:
    services:
      - a
      - b
    networks:
      # ...
    volumes:
      # ...

  two:
    services:
      # ...
```
