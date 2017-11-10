Environment files
=================

What is it?
~~~~~~~~~~~~

Environment files allow you to **parameterize your deployment** as you want, by **substituting values in Jinja template files**, often used for configuration for your services, or to directly **inject environment variables** in your containers.

How does it work?
~~~~~~~~~~~~~~~~~~

Starting from **docknv 4**, environment files are now in the *YAML* format.

It allows some useful features.

Environment files **inheritance**
---------------------------------

For example, you can make a **default** environment file for all your deployments and only override the required  variables.

.. code-block:: yaml
   :caption: default.env.yml

    environment:
      my_value: 1
      my_second_value: Toto

    # Known values:
    #   - my_value = 1
    #   - my_second_value = Toto

.. code-block:: yaml
   :caption: inclusion.env.yml

    imports:
      - default
    environment:
      my_value: 2
      my_other_value: Tata

    # Known values:
    #   - my_value = 2 (overriden)
    #   - my_second_value = Toto (from default)
    #   - my_other_value = Tata


Variable **interpolation**
----------------------------

Thanks to a simple string interpolation system, you can define variables containing other variables.
But these variables **can be overriden** over the imported files, for easy reuse of the existing variables.

Here is an example:

.. code-block:: yaml
   :caption: default.env.yml

    environment:
      my_var: test
      my_var_concat: Hello ${my_var}
      my_var_double: ${my_var} + ${my_var} = ${my_var}${my_var}

    # Known values:
    #   - my_var = test
    #   - my_var_concat: Hello test
    #   - my_var_double: test + test = testtest

.. code-block:: yaml
   :caption: inclusion.env.yml

    imports:
      - default
    environment:
      my_var: test2

    # Known values:
    #   - my_var = test2
    #   - my_var_concat = Hello test2
    #   - my_var_double: test2 + test2 = test2test2
