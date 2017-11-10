Architecture
============

Project structure
~~~~~~~~~~~~~~~~~

To use **Docknv**, you need to respect the following structure, all
contained in a root folder:

-  **commands**: The location of your custom docknv commands. *(optional)*
-  **composefiles**: The location of your Docker Compose files.
-  **data**: Your project data, organized in three different folders:

   -  **files**: Static files and Jinja2 templates imported via volumes
      should be stored here, with one folder per container
   -  **standard**: Here you can put private files to be imported

-  **envs**: The location of your environment configuration files,
   ending with ``.env.py`` (example for *debug*, the filename is
   ``debug.env.py``). By default, there is always a ``default.env.py``.
-  **images**: The location of your Docker images, one folder per
   container. You should always use the "building" way (instead of the
   direct fetching) when including new Docker images in your Compose
   files.
-  **config.yml**: The main Docknv configuration file for your project.
