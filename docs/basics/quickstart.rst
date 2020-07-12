============
Full example
============
.. warning::  This is incomplete and will be extended to include validation and other,
           more complex patterns.

.. note:: Finished example `can be found at github <https://github.com/mlga/schematics-proto3/tree/master/examples/01_overview_example>`_.


Given following protobuf definition and ``student_pb2.py`` Python module:

.. code-block:: protobuf
  :linenos:

  syntax = "proto3";

  import "google/protobuf/wrappers.proto";

  package overview_example;

  enum Grade {
      UNKNOWN = 0;
      // others...
      B = 5;
      A = 6;
  }

  message Student {
      message CourseGrade {
          string course_id = 1;
          Grade grade = 2;
      }

      uint32 id = 1;
      google.protobuf.StringValue name = 2;
      repeated CourseGrade grades = 3;
  }


We can declare following ``Model`` classes, which reflect the structure of above message:

.. code-block:: python
   :linenos:

   from schematics import types

   from schematics_proto3 import Model
   from schematics_proto3 import types as pbtypes
   from schematics_proto3.enum import ProtobufEnum

   import student_pb2 as pb2  # noqa


   class Grade(ProtobufEnum, protobuf_enum=pb2.Grade):
       pass


   class CourseGrade(Model, protobuf_message=pb2.Student.CourseGrade):
       course_id = types.StringType()
       grade = pbtypes.EnumType(
           Grade,
           unset_variant=pb2.Grade.UNKNOWN,
       )


   class StudentModel(Model, protobuf_message=pb2.Student):
       id = types.IntType()
       name = pbtypes.StringWrapperType()
       grades = pbtypes.RepeatedType(
           pbtypes.MessageType(CourseGrade),
       )

And now, we can instantiate ``StudentModel`` class directly from Protobuf message:


.. code-block:: python
   :linenos:

   # Build a student message, normally that comes through the wire
   msg = pb2.Student()
   msg.id = 42
   msg.name.value = 'Jon Doe'
   msg.grades.extend([
        pb2.Student.CourseGrade(course_id='maths', grade=pb2.Grade.A),
        pb2.Student.CourseGrade(course_id='physics', grade=pb2.Grade.A),
   ])

   # Create StudentModel instance, loading protobuf message
   model = StudentModel.load_protobuf(msg)
   model.validate()

   # Inspect instance attributes
   print('Student ID:', model.id)
   # Student ID: 42
   print('Student name:', model.name)
   # Student name: Jon Doe
   for grade in model.grades:
       print(f'`{grade.course_id}` grade:', grade.grade)
   # `maths` grade: A
   # `physics` grade: A

   # Export instance to dict
   print(model.to_native())
   # {'id': 42, 'name': 'Jon Doe', 'grades': [{'course_id': 'maths', 'grade': 'A'}, {'course_id': 'physics', 'grade': 'A'}]}
