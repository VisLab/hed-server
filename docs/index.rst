HED online tools
================


.. sidebar:: Quick links
   
   * `HED online tools <https://hedtools.org/hed>`_

   * `HED homepage <https://www.hedtags.org/>`_ 
   
   * `HED resources <https://www.hedtags.org/hed-resources>`_

   * `HED schema browser <https://www.hedtags.org/hed-schema-browser>`_

   * `HED specification <https://www.hedtags.org/hed-specification>`_ 

   * `Python HEDTools <https://hed-python.readthedocs.io/>`_ 

   * `Table-remodeler <https://www.hedtags.org/table-remodeler>`_

Welcome to the HED online tools documentation! This package provides web-based interfaces and REST API services for working with **Hierarchical Event Descriptors (HED)** - a standardized framework for annotating events and experimental metadata in neuroscience and beyond.

What is HED?
------------

HED is a standardized vocabulary and annotation framework designed to systematically describe events in experimental data, particularly neuroimaging and behavioral data. It's integrated into major neuroimaging standards:

* `BIDS <https://bids.neuroimaging.io/>`_ (Brain Imaging Data Structure)
* `NWB <https://www.nwb.org/>`_ (Neurodata Without Borders)

Key features
------------

* **Web interface**: Browser-based tools for easy HED operations
* **REST API**: Programmatic access to all HED services
* **Validation**: Verify HED annotations against official schemas
* **Transformation**: Convert between different HED formats
* **BIDS support**: Process BIDS datasets with HED annotations
* **Multiple formats**: Work with JSON sidecars, TSV files, Excel spreadsheets
* **Schema operations**: Validate, convert, and compare HED schemas
* **Docker support**: Easy local deployment with Docker containers

Getting started
---------------

.. toctree::
   :maxdepth: 2

   Introduction <introduction>

Using HED online tools
----------------------

.. toctree::
   :maxdepth: 2

   User guide <user_guide>

Local deployment
----------------

.. toctree::
   :maxdepth: 2

   Installation <installation>

API documentation
-----------------

.. toctree::
   :maxdepth: 2

   API reference <api/index>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
