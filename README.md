# docknv

## Introduction

### What is it ?

### Multiple Compose templates ?

### Schemas

### Lifecycles

## Configuration syntax

```
templates:
  # blablabla

schemas:
  # blablabla

lifecycles:
  # blablabla
```

### 1. Templates

You can merge multiple compose sources.  
Just list all of them in here.

*Example:*

```
templates:
  - ./templates/main.yml
  - ./templates/plugin.yml
```

### 2. Schemas

Here you precise your Compose schemas, depending on your needs for the lifecycles to come.  
For example, you may have one main schema, one small plugin schema, and a complete schema with both.  
For each schema, you precise the needed local volumes and services.  

*Example:*

```
schemas:
  main:
    volumes:
      - vol1
    services:
      - main1
      - main2

  plugin:
    volumes:
      - pluginVol1
    services:
      - pluginService1

  full:
    includes:
      - main
      - plugin
```

### 3. Lifecycles

This is where you decide what to do with your containers.  
For each lifecycle, you can precise **handlers** with **commands** or **actions**.

*Example 1: Simple "start all" lifecycle*

```
lifecycles:
  start_main:
    schema: main
    action: start
```

This lifecycle will start all machines from the *main* schema.

*Example 2: Start all and execute one action before*

```
lifecycles:
  prepare_main:
    schema: main
    action: start
    handlers:
      main1:
        command: bash /prepare.sh
```

In this example, all machines will be started, with one override for the *main1* machine, which will execute a *bash* script, then will boot normally.
