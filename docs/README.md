# Estuary API Documentation

## Build the Docs

To build and run the docs, run the following commands **in the docs directory**:
```
$ make clean
$ make html
$ google-chrome _build/html/index.html
```

## Expanding the Docs

To add a new section:
* Create an rst file in the docs folder, such as `models.rst`, where models is the name of the new section, with the following format:
```
:github_url: https://github.com/release-engineering/estuary-api/path/to/section

=======
Models
=======

.. automodule:: path.to.section
   :members:
```
* In the `docs/index.rst` file, in the toctree, add the name of the section (in this example, models)

To document a new model file:
* In `docs/models.rst`, add the following code:
```
Model Name
==========
.. automodule:: estuary.models.model_name
   :members:
   :undoc-members:
```

*Note that it is not necessary to document new methods in classes that are already documented, as Sphinx will generate documentation for them automatically*