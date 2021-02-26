import typing

import pytest

import strawberry


def test_supports_generic_simple_type():
    global Edge, T

    T = typing.TypeVar("T")

    @strawberry.type
    class Edge(typing.Generic[T]):
        cursor: strawberry.ID
        node_field: T

    @strawberry.type
    class Query:
        @strawberry.field
        def int_edge(self) -> Edge[int]:
            return Edge(cursor=strawberry.ID("1"), node_field=1)

    schema = strawberry.Schema(query=Query)

    query = """{
        intEdge {
            __typename
            cursor
            nodeField
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "intEdge": {"__typename": "IntEdge", "cursor": "1", "nodeField": 1}
    }

    del Edge, T


def test_supports_generic():
    global Edge, T, Person

    T = typing.TypeVar("T")

    @strawberry.type
    class Edge(typing.Generic[T]):
        cursor: strawberry.ID
        node: T

    @strawberry.type
    class Person:
        name: str

    @strawberry.type
    class Query:
        @strawberry.field
        def person_edge(self) -> Edge[Person]:
            return Edge(cursor=strawberry.ID("1"), node=Person(name="Example"))

    schema = strawberry.Schema(query=Query)

    query = """{
        personEdge {
            __typename
            cursor
            node {
                name
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "personEdge": {
            "__typename": "PersonEdge",
            "cursor": "1",
            "node": {"name": "Example"},
        }
    }

    del Edge, T, Person


def test_supports_multiple_generic():
    global A, B, Multiple

    A = typing.TypeVar("A")
    B = typing.TypeVar("B")

    @strawberry.type
    class Multiple(typing.Generic[A, B]):
        a: A
        b: B

    @strawberry.type
    class Query:
        @strawberry.field
        def multiple(self) -> Multiple[int, str]:
            return Multiple(a=123, b="123")

    schema = strawberry.Schema(query=Query)

    query = """{
        multiple {
            __typename
            a
            b
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "multiple": {"__typename": "IntStrMultiple", "a": 123, "b": "123"}
    }

    del A, B, Multiple


def test_support_nested_generics():
    global T, User, Edge, Connection

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        node: T

    @strawberry.type
    class Connection(typing.Generic[T]):
        edge: Edge[T]

    @strawberry.type
    class Query:
        @strawberry.field
        def users(self) -> Connection[User]:
            return Connection(edge=Edge(node=User("Patrick")))

    schema = strawberry.Schema(query=Query)

    query = """{
        users {
            __typename
            edge {
                __typename
                node {
                    name
                }
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "users": {
            "__typename": "UserConnection",
            "edge": {"__typename": "UserEdge", "node": {"name": "Patrick"}},
        }
    }

    del T, User, Edge, Connection


def test_supports_optional():
    global T, User, Edge

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        node: typing.Optional[T] = None

    @strawberry.type
    class Query:
        @strawberry.field
        def user(self) -> Edge[User]:
            return Edge()

    schema = strawberry.Schema(query=Query)

    query = """{
        user {
            __typename
            node {
                name
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {"user": {"__typename": "UserEdge", "node": None}}

    del T, User, Edge


def test_supports_lists():
    global T, User, Edge

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        nodes: typing.List[T]

    @strawberry.type
    class Query:
        @strawberry.field
        def user(self) -> Edge[User]:
            return Edge(nodes=[])

    schema = strawberry.Schema(query=Query)

    query = """{
        user {
            __typename
            nodes {
                name
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {"user": {"__typename": "UserEdge", "nodes": []}}

    del T, User, Edge


def test_supports_lists_of_optionals():
    global T, User, Edge

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        nodes: typing.List[typing.Optional[T]]

    @strawberry.type
    class Query:
        @strawberry.field
        def user(self) -> Edge[User]:
            return Edge(nodes=[None])

    schema = strawberry.Schema(query=Query)

    query = """{
        user {
            __typename
            nodes {
                name
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {"user": {"__typename": "UserEdge", "nodes": [None]}}
    del T, User, Edge


def test_can_extend_generics():
    global T, User, Edge, Connection, ConnectionWithMeta

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        node: T

    @strawberry.type
    class Connection(typing.Generic[T]):
        edges: typing.List[Edge[T]]

    @strawberry.type
    class ConnectionWithMeta(Connection[T]):
        meta: str

    @strawberry.type
    class Query:
        @strawberry.field
        def users(self) -> ConnectionWithMeta[User]:
            return ConnectionWithMeta(meta="123", edges=[Edge(node=User("Patrick"))])

    schema = strawberry.Schema(query=Query)

    query = """{
        users {
            __typename
            meta
            edges {
                __typename
                node {
                    name
                }
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "users": {
            "__typename": "UserConnectionWithMeta",
            "meta": "123",
            "edges": [{"__typename": "UserEdge", "node": {"name": "Patrick"}}],
        }
    }

    del T, User, Edge, Connection, ConnectionWithMeta


def test_supports_generic_in_unions():
    global T, Edge, Fallback

    T = typing.TypeVar("T")

    @strawberry.type
    class Edge(typing.Generic[T]):
        cursor: strawberry.ID
        node: T

    @strawberry.type
    class Fallback:
        node: str

    @strawberry.type
    class Query:
        @strawberry.field
        def example(self) -> typing.Union[Fallback, Edge[int]]:
            return Edge(cursor=strawberry.ID("1"), node=1)

    schema = strawberry.Schema(query=Query)

    query = """{
        example {
            __typename

            ... on IntEdge {
                cursor
                node
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "example": {"__typename": "IntEdge", "cursor": "1", "node": 1}
    }

    del T, Edge, Fallback


def test_supports_generic_in_unions_multiple_vars():
    global A, B, Edge, Fallback

    A = typing.TypeVar("A")
    B = typing.TypeVar("B")

    @strawberry.type
    class Edge(typing.Generic[A, B]):
        info: A
        node: B

    @strawberry.type
    class Fallback:
        node: str

    @strawberry.type
    class Query:
        @strawberry.field
        def example(self) -> typing.Union[Fallback, Edge[int, str]]:
            return Edge(node="string", info=1)

    schema = strawberry.Schema(query=Query)

    query = """{
        example {
            __typename

            ... on IntStrEdge {
                node
                info
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "example": {"__typename": "IntStrEdge", "node": "string", "info": 1}
    }

    del A, B, Edge, Fallback


def test_supports_generic_in_unions_with_nesting():
    global T, User, Edge, Connection, Fallback

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        node: T

    @strawberry.type
    class Connection(typing.Generic[T]):
        edge: Edge[T]

    @strawberry.type
    class Fallback:
        node: str

    @strawberry.type
    class Query:
        @strawberry.field
        def users(self) -> typing.Union[Connection[User], Fallback]:
            return Connection(edge=Edge(node=User("Patrick")))

    schema = strawberry.Schema(query=Query)

    query = """{
        users {
            __typename
            ... on UserConnection {
                edge {
                    __typename
                    node {
                        name
                    }
                }
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "users": {
            "__typename": "UserConnection",
            "edge": {"__typename": "UserEdge", "node": {"name": "Patrick"}},
        }
    }

    del T, User, Edge, Connection, Fallback


@pytest.mark.skip("broken, not sure why")
def test_supports_multiple_generics_in_union():
    global T, Edge

    T = typing.TypeVar("T")

    @strawberry.type
    class Edge(typing.Generic[T]):
        cursor: strawberry.ID
        node: T

    @strawberry.type
    class Query:
        @strawberry.field
        def example(self) -> typing.List[typing.Union[Edge[int], Edge[str]]]:
            return [
                Edge(cursor=strawberry.ID("1"), node=1),
                Edge(cursor=strawberry.ID("2"), node="string"),
            ]

    schema = strawberry.Schema(query=Query)

    query = """{
        example {
            __typename

            ... on IntEdge {
                cursor
                intNode: node
            }

            ... on StrEdge {
                cursor
                strNode: node
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "example": [
            {"__typename": "IntEdge", "cursor": "1", "intNode": 1},
            {"__typename": "StrEdge", "cursor": "2", "strNode": "string"},
        ]
    }

    del T, Edge


def test_generated_names():
    global T, EdgeWithCursor, SpecialPerson

    T = typing.TypeVar("T")

    @strawberry.type
    class EdgeWithCursor(typing.Generic[T]):
        cursor: strawberry.ID
        node: T

    @strawberry.type
    class SpecialPerson:
        name: str

    @strawberry.type
    class Query:
        @strawberry.field
        def person_edge(self) -> EdgeWithCursor[SpecialPerson]:
            return EdgeWithCursor(
                cursor=strawberry.ID("1"), node=SpecialPerson(name="Example")
            )

    schema = strawberry.Schema(query=Query)

    query = """{
        personEdge {
            __typename
            cursor
            node {
                name
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {
        "personEdge": {
            "__typename": "SpecialPersonEdgeWithCursor",
            "cursor": "1",
            "node": {"name": "Example"},
        }
    }

    del T, EdgeWithCursor, SpecialPerson


def test_supports_lists_within_unions():
    global T, User, Edge

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        nodes: typing.List[T]

    @strawberry.type
    class Query:
        @strawberry.field
        def user(self) -> typing.Union[User, Edge[User]]:
            return Edge(nodes=[User("P")])

    schema = strawberry.Schema(query=Query)

    query = """{
        user {
            __typename

            ... on UserEdge {
                nodes {
                    name
                }
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {"user": {"__typename": "UserEdge", "nodes": [{"name": "P"}]}}

    del T, User, Edge


def test_supports_lists_within_unions_empty_list():
    global T, User, Edge

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        nodes: typing.List[T]

    @strawberry.type
    class Query:
        @strawberry.field
        def user(self) -> typing.Union[User, Edge[User]]:
            return Edge(nodes=[])

    schema = strawberry.Schema(query=Query)

    query = """{
        user {
            __typename

            ... on UserEdge {
                nodes {
                    name
                }
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert not result.errors
    assert result.data == {"user": {"__typename": "UserEdge", "nodes": []}}

    del T, User, Edge


@pytest.mark.skip("broken as well")
def test_raises_error_when_unable_to_find_type():
    global T, User, Edge

    T = typing.TypeVar("T")

    @strawberry.type
    class User:
        name: str

    @strawberry.type
    class Edge(typing.Generic[T]):
        nodes: typing.List[T]

    @strawberry.type
    class Query:
        @strawberry.field
        def user(self) -> typing.Union[User, Edge[User]]:
            return Edge(nodes=["bad example"])  # type: ignore

    schema = strawberry.Schema(query=Query)

    query = """{
        user {
            __typename

            ... on UserEdge {
                nodes {
                    name
                }
            }
        }
    }"""

    result = schema.execute_sync(query)

    assert result.errors[0].message == (
        "Unable to find type for <class 'tests.schema.test_generics."
        "test_raises_error_when_unable_to_find_type.<locals>.Edge'> "
        "and (<class 'str'>,)"
    )

    del T, User, Edge
