---
title: Book
type: MODEL_TEMPLATE
status: new
---

# Model: Book

## Attributes:
### title
- **Type**: str
- **Description**: The title of the book.
- **Examples**:
  - "Harry Potter and the Philosopher's Stone"

### author
- **Type**: [[models/Author.md|Author]]
- **Description**: The author of the book.

### genres
- **Type**: List[str]
- **Description**: The genres the book belongs to.
- **Examples**:
  - "Fantasy"
  - "Adventure"
