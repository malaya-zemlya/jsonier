# jsonier
A Python library for converting JSON code to object instances and back.

To declare an object that can be converted to and from JSON:

```
from jsonier import jsonified, Field

@jsonified
class Person:
    first = Field(str, required=True)
    last = Field(str, required=True)
    age = Field(int)
    is_working = Field(bool)
```

Now you can read this object from JSON like so:

```python
data = """
{"first": "Bob", "last": "Ross", age: 50, "is_working": true}
"""
jdata = json.loads(data)
p = Person.load(jdata)

print(p.first) # Bob
print(p.last) # Ross

```
You can also parse a string directly:

```python
data = """
{"first": "Bob", "last": "Ross", age: 50, "is_working": true}
"""
p = Person.loads(data)
```

To convert an object to JSON:

```python
p = Person(first="Alice", last="Smith", age=30)
print(p.dump()) 
```

```
{'first-name': 'Alice', 'surname': 'Smith', 'age': 30}
```

```python
print(p.dumps(indent=2))
```

```
{
  "first-name": "Alice",
  "surname": "Smith",
  "age": 30
}
```


