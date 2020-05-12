# 01_overview_example
Basic example of loading simple `Student` Protobuf message using `Model` class.

To run this, just execute:
```bash
$ python main.py
Student ID: 42
Student name: Jon Doe
`maths` grade: Grade.A
`physics` grade: Grade.A
{'id': 42, 'name': 'Jon Doe', 'grades': [{'course_id': 'maths', 'grade': 'A'}, {'course_id': 'physics', 'grade': 'A'}]}
```

To generate Python module from `.proto` definition, run:

```bash
protoc -I . --python_out . student.proto
``` 
