Architecture
============

This section introduces the architecture of ``ucdp``.

.. contents::
  :local:

Overview
~~~~~~~~

.. figure:: arch.drawio.png
   :alt: Architecture Overview

The base idea of `ucdp` is to describe the chip `Modules`_,
their intend, hierarchy and:

* `Identifier`_ (:any:`Port`, :any:`Signal`, :any:`Parameter`) and their `Types`_

Types
~~~~~

Identifier
~~~~~~~~~~

Expression Engine
~~~~~~~~~~~~~~~~~

Assigns
~~~~~~~

Flip-Flop
---------

Multiplexer
-----------

Router
------

Modules
~~~~~~~

Loader
~~~~~~

FileSet-Engine
~~~~~~~~~~~~~~

Documentation
~~~~~~~~~~~~~

.. -----------------

.. * Documentation Container
..   * :any:`doc`

.. * Multiplexer

.. * Types

..   * :any:`clkrsttypes`
..   * :any:`descriptivestruct`
..   * :any:`enumtypes`
..   * :any:`structtypes`
..   * :any:`types`

.. * Identifier
..   * Signal
..   * SignalTracer
..   * Namespace
..   * Ident
..   * Parameter

.. * Expressions

.. * FlipFlop
.. * Router
.. * Mux
.. * Assigns
.. * Multiplexer
.. * Loader
..   * IcTop

.. * Module + Config

..   * :any:`basemod` - Base Class for all module flavours
..   * :any:`config`
..       * :any:`BaseConfig`
..       * :any:`AConfig`
..       * :any:`VersionConfig`
..       * :any:`UniqueConfig`

.. * Router

..   * :any:`assigns` - Port and Signal Assignment Handling

.. * Gen
.. * Module Iterator
.. * Orientation
.. * Slice
.. * Test

.. * FileList Support

.. Exclude List

.. * File Handling
.. * Coverage Exclude
.. * Engine



.. * :any:`expr`
.. * :any:`fileset`
.. * :any:`filesetrule`
.. * :any:`flipflop`
.. * :any:`gen`
.. * :any:`hdlruleset`
.. * :any:`ictop`
.. * :any:`ictopspec`
.. * :any:`ident`
.. * :any:`__init__`
.. * :any:`loader`
.. * :any:`moditer`
.. * :any:`mods`
.. * :any:`modutil`
.. * :any:`mux`
.. * :any:`namespace`
.. * :any:`nameutil`
.. * :any:`orient`
.. * :any:`param`
.. * :any:`router`
.. * :any:`signal`
.. * :any:`signaltracer`
.. * :any:`slices`
.. * :any:`svutil`
.. * :any:`test`
.. * :any:`typeiter`
.. * :any:`types`
.. * :any:`typeutil`
.. * :any:`util`
.. * :any:`version`


Utilties
~~~~~~~~

This section lists all external libraries and their usage

.. list-table:: Our Dependencies
   :widths: 25 75
   :header-rows: 1

   * - Name
     - Usage
   * - :any:`attrs`
     - | **Datamodel.**
       | All Data Classes base on :any:`attrs.define`.
       | We only use what :any:`ucdp.attrs` serves us, to handle :any:`attrs` API changes gracefully.
   * - ``mementos``
     - | **Caching.**
       | Read-Only objects with the same idenitdy (arguments) are just created once.
       | We save memory, memory and memory. And we gain speed and speed.
   * - `tabulate <https://pypi.org/project/tabulate/>`_
     - | **Table Formatting.**
       | We need to present a lot of data.
       | `tabulate <https://pypi.org/project/tabulate/>`_ creates nice tables in many formats.
   * - :any:`aligntext`
     - | **Code Formatting.**
       | Readable program code should be aligned.
       | During Code Generation :any:`aligntext` handles that for us.
   * - :any:`humannum`
     - | **Number Formatting.**
       | Designer like binary related numbers to be presented in :any:`humannum.bin_`,
       | :any:`humannum.hex_` or :any:`humannum.bytes` notation.
       | :any:`humannum` extends python builtin numbers by that feature.
   * - :any:`outputfile`
     - | **Timestamp Preserving File Writing.**
       | File timestamps are key when it comes to build systems.
       | :any:`outputfile.open_` preserves the timestamp of the generated file
       | on identical file content.
   * - :any:`makolator`
     - | **Mako Templates Extended.**
       | Code generation is much easier with a template engine.
       | `mako <https://www.makotemplates.org/>`_ is fast, allows python code in templates and supports inheritance.
       | :any:`makolator` uses :any:`outputfile` and simplifies the use of `mako <https://www.makotemplates.org/>`_.
   * - :any:`uniquer`
     - | **Utility to remove duplicates.**
       | Remove duplicates from iterables.
   * - `case-converter <https://pypi.org/project/case-converter/>`_
     - | **Name Converter.**
       | Convert names between different name schemes:
       | ``PascalCase``, ``camelCase``, ``snake_case``,
   * - :any:`icutil`
     - | **IC Utilties.**
       | Helper for binary related chip infrastructure.
   * - :any:`matchor`
     - | **String Pattern Matching.**
