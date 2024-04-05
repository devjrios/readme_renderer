Readme Renderer
===============

.. image:: https://github.com/devjrios/readme_renderer/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/devjrios/readme_renderer/actions/workflows/ci.yml

Readme Renderer is a library that will safely render arbitrary
``README`` files into HTML. It can handle Markdown,
reStructuredText (``.rst``), and plain text.


Check Description Locally
-------------------------

Test this README (or any personal file):

.. code:: bash

   python3 -m readme_renderer -f rst -o README.html README.rst && \
   xdg-open README.html
