# Internals

In this document \_ means a trailing space

The example is

- cli
  - a
  - aaaa
  - b
  - c
  - d
  - zzz
    - zebedee
    - zebra
    - zoo


## The forwards direction

Mostly handled by this code.

`if self.direction == 'forwards' and len(document_text) >= self.go_to_next_node_at_position and self.go_to_next_node_at_position > 0:`

`set cl`

- len(document.text) = 6
- we set next-node to character position 7
- currentNode is root
- lastpart is the string split by string (taking account of quoted strings) and is `cl`


`set cli`

- len(document.text) = 7
- we reset next-node at character position to 0
- we set parent-node at charcater to position to 7
- set currentNode to `/cli`
- previous node is now `/`

`set cli_`

- ipython kicks in autocomplete, we are doing `_children` on currentNode and find what we have avaialble.
- lastpart is a blank string ''
- len(document.text) = 8

`set cli z`

- **once we get to a single child option - zzz is the option**
- we reset next node at character position to 11 (set cli + zzz == 11)
- currentNode is `/cli`
- previousNode is `/`

`set cli zzz`

- we reset next-node at character position o 0
- we set parent-node at charcater position to 11
- currentNode is `/cli/zzz`
- previousNode is `/cli`
