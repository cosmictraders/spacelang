.. Spacelang documentation master file, created by
   sphinx-quickstart on Wed May 24 20:27:31 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Spacelang's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   structure


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

First create a python file with the following code:

.. code:: python

   File(load_text(open("example.yml"))).run(s.get_session("[YOUR TOKEN HERE]"))

Create ``example.yml`` in your working directory and it'll run if you run the python file!
