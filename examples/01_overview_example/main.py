# -*- coding:utf-8 -*-
import os
import sys

from schematics import types

from schematics_proto3 import Model
from schematics_proto3 import types as pbtypes
from schematics_proto3.enum import ProtobufEnum

# hack import path so we can import student definitions

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import student_pb2 as pb2  # noqa


class Grade(ProtobufEnum, protobuf_enum=pb2.Grade):
    """
    Grade enum, class is constructed automatically by inspection of
    protobuf enum.
    """
    pass


class CourseGrade(Model, protobuf_message=pb2.Student.CourseGrade):
    """
    Model of a grade, contains course_id and grade.
    """
    course_id = types.StringType()
    grade = pbtypes.EnumType(
        Grade,
        unset_variant=pb2.Grade.UNKNOWN,
    )


class StudentModel(Model, protobuf_message=pb2.Student):
    """
    Model of a student.
    """
    id = types.IntType()
    name = pbtypes.StringWrapperType()
    grades = pbtypes.RepeatedType(
        pbtypes.MessageType(CourseGrade),
    )


if __name__ == '__main__':
    # Build a student message
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
    print('Student name:', model.name)
    for grade in model.grades:
        print(f'`{grade.course_id}` grade:', grade.grade)

    # Export instance to dict
    print(model.to_native())
