"""Builds the structured OOP-extraction prompt for the AI."""
from __future__ import annotations

SUPPORTED_LANGUAGES = ["Python", "C++", "Java", "C#", "TypeScript"]

LANGUAGE_RULES = {
    "Python": """
- Use `class` definitions with `__init__` constructors.
- Private attributes start with a single underscore (e.g. `self._title`).
- Use type hints for parameters and return types where useful.
- Use `list[X]` for one-to-many or many-to-many relationships.
- Inheritance: `class Child(Parent):`.
- Composition: create the child object inside `__init__`.
- Aggregation/Association: accept the related object as a constructor arg.
- Provide method bodies as `pass` or a brief placeholder, no full logic.
""",
    "C++": """
- Use `class` with explicit `public:` and `private:` sections.
- Private data members suffixed with `_` (e.g. `std::string title_;`).
- Provide constructor declarations (and default destructor when relevant).
- Use `std::vector<T>` for one-to-many / many-to-many.
- Inheritance: `class Child : public Parent { ... };`.
- Composition: store the child as a value member.
- Aggregation/Association: store as a pointer or reference.
- Method bodies may be left as `// TODO` inside `{ }`.
- Include `#include <string>` and `#include <vector>` at the top.
""",
    "Java": """
- All attributes `private`. Methods `public` unless they are helpers.
- Provide constructors.
- Use `List<T>` (java.util.List / ArrayList) for collections.
- Inheritance: `class Child extends Parent { ... }`.
- Composition: instantiate inside the constructor.
- Aggregation/Association: pass as a constructor parameter.
- Include `import java.util.*;` at the top.
- Method bodies: `// TODO`.
""",
    "C#": """
- Private fields prefixed with `_` (e.g. `private string _title;`).
- Use auto-properties (`public int Id { get; set; }`) where natural.
- Use `List<T>` for collections (`using System.Collections.Generic;`).
- Inheritance: `class Child : Parent { ... }`.
- Composition: instantiate inside the constructor.
- Aggregation/Association: inject via constructor.
- Method bodies: `// TODO`.
""",
    "TypeScript": """
- Use `class` with `private` / `public` modifiers on members.
- Strong typing: `private title: string;`, `private items: Item[] = [];`.
- Use `T[]` for one-to-many / many-to-many.
- Inheritance: `class Child extends Parent { ... }`.
- Composition: instantiate inside the constructor.
- Aggregation/Association: inject via constructor parameters.
- Method bodies: `// TODO`.
""",
}


SYSTEM_PROMPT = (
    "You are an expert software architect and OOP designer. "
    "You always respond in the exact section format requested, with no extra prose, "
    "no greetings, and no markdown code fences around the section headers."
)


def build_prompt(description: str, language: str) -> str:
    if language not in LANGUAGE_RULES:
        language = "Python"

    rules = LANGUAGE_RULES[language].strip()

    return f"""Analyse the following software description and produce an object-oriented
design plus a code skeleton in {language}.

SOFTWARE DESCRIPTION:
\"\"\"
{description.strip()}
\"\"\"

OOP PRINCIPLES TO APPLY:
- Encapsulation, abstraction, modularity, low coupling, high cohesion.
- Prefer composition over inheritance unless inheritance is clearly justified.
- Avoid redundant or trivial classes.
- Detect multiplicity (one-to-one, one-to-many, many-to-many).

LANGUAGE-SPECIFIC RULES ({language}):
{rules}

OUTPUT FORMAT — respond with EXACTLY these sections, in this order, using the
section headers verbatim. Do not wrap headers in code fences. Do not add any
text before the first header or after the last section.

### CLASSES
One class name per line.

### ATTRIBUTES
For each class, a block of the form:
ClassName:
  - attributeName : DataType
  - attributeName : DataType

### METHODS
For each class, a block of the form:
ClassName:
  - methodName()
  - methodName()

### RELATIONSHIPS
One relationship per line, using these symbols:
  <|--   inheritance (Child <|-- Parent means Parent is parent of Child; write Parent <|-- Child)
  -->    association
  o--    aggregation
  *--    composition
  ..>    dependency
Format:
  ClassA SYMBOL ClassB : short description (multiplicity if relevant)

### CODE
A single fenced code block in {language} containing the full skeleton with
boilerplate (constructors, private attributes, method stubs, relationship
wiring). Use ```{language.lower()} on the opening fence.

### PLANTUML
A single fenced code block starting with ```plantuml containing a complete,
valid PlantUML class diagram. The diagram MUST start with:

@startuml
skinparam classAttributeIconSize 0
skinparam linetype ortho
skinparam nodesep 80
skinparam ranksep 80

…then class definitions with attributes and methods, then relationships using
the symbols above, then end with @enduml. Keep the diagram clean: logical
grouping, minimal crossing lines.
"""
