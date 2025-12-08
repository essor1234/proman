# app/schemas/__init__.py

from .todo import (
    # Todo
    Todo as TodoSchema,
    TodoCreate,
    TodoUpdate)

from .moscow import (
    # Moscow
    Moscow as MoscowSchema,
    MoscowCreate,
    MoscowUpdate)

from .task import (
    # Task
    Task as TaskSchema,
    TaskCreate,
    TaskUpdate
)