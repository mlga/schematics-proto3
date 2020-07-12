.. schematics-proto3 documentation master file, created by
   sphinx-quickstart on Sat Apr 11 18:04:04 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================
schematics-proto3
=================
Built upon `Schematics <https://schematics.readthedocs.io>`_ - *Python Data
Structures for Humans™*, ``schematics-proto3`` brings the awesome features
of `Schematics <https://schematics.readthedocs.io>`_ to Protobuf 3 world.

.. contents::
   :local:
   :depth: 1

.. note::  Library is currently in **WORK IN PROGRESS** state.

           What is implemented and tested:

           #. Loading Protobuf 3 messages to Model instances.

              * for most of the Protobuf 3 types, including
                `wrappers <https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto>`_, ``repeated`` and ``oneof`` fields
           #. Validation and structured error messages.

           To be done:

           #. Serializing Model instances to Protobuf 3 messages.
           #. Enum type.
           #. Make the library more user-friendly.
           #. Schematics "roles".

Motivation
==========
As good and widely supported as it is, Protobuf 3 still has some quirks
which can make working with it painful and repetitive. Especially, building
complex gRPC services might reveal a number of deficiencies in available tooling.

``schematics-proto3`` aims to address this problem, in particular:

* [`#359 <https://github.com/protocolbuffers/protobuf/issues/359>`_]
  default values and testing if a field is set in v3

  `There is a workaround for this <https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto>`_,
  ``schematics-proto3`` incorporates wrapper types to hide nested messages underneath.

* no proper data handling library

  Comparing to Serializers in Django Rest Framework or Marshmallow, there seems to be no full
  fledged serialization / validation / deserialization library for Protobuf 3.
  Thanks to `Schematics <https://schematics.readthedocs.io>`_, ``schematics-proto3``
  is able to provide:

  * declarative models
  * custom validation functions
  * structured error messages (currently only as Python dict)

Example
=======
Let's take `Schematics example <https://schematics.readthedocs.io/en/latest/#example>`_ and modify it to work with Protobuf.

We have a following Protobuf message (and ``person_pb2`` Python module).

.. code-block:: protobuf
  :linenos:

  syntax = "proto3";

  import "google/protobuf/wrappers.proto";

  package example;

  message Person {
      google.protobuf.StringValue name = 1;
      google.protobuf.StringValue website = 2;
  }

And reflect above message in ``Model`` class.

.. code-block:: python
   :linenos:

   from schematics_proto3 import Model
   from schematics_proto3 import types as pbtypes

   import person_pb2 as pb2


   class PersonModel(Model, protobuf_message=pb2.Person):
       name = pbtypes.StringWrapperType()
       website = pbtypes.StringWrapperType()


Let's load some data.

.. code-block:: python
   :linenos:

   msg = pb2.Person()
   msg.name.value = 'Jon Doe'
   msg.website.value = 'https://example.com'

   model = PersonModel.load_protobuf(msg)
   model.validate()

   assert model.name == 'Jon Doe'
   assert model.website == 'https://example.com'

   assert model.to_native() == {'name': 'Jon Doe', 'website': 'https://example.com'}

Not setting a field will give you an ``Unset``.

.. code-block:: python
   :linenos:

   from schematics_proto3.unset import Unset

   msg = pb2.Person()
   msg.name.value = 'Jon Doe'

   model = PersonModel.load_protobuf(msg)
   model.validate()

   assert model.name == 'Jon Doe'
   assert model.website is Unset


Installation
============
Currently possible only from repository. Let me know if you want to use it, I
will create a PyPI project.

.. toctree::
   :glob:
   :hidden:
   :maxdepth: 2
   :caption: Basics

   Overview <self>
   basics/*

.. toctree::
   :glob:
   :hidden:
   :maxdepth: 2
   :caption: User's guide

   guide/*

.. toctree::
   :glob:
   :hidden:
   :maxdepth: 2
   :caption: API reference

   api/*
