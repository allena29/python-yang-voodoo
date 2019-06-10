# Internals

 `set bronze silver gold platinum parts-1=platinum len(text)=31 gotoparent=22`

  - `document.text` = `set bronze silver gold platinum`
  - `parts` regular expression used to find the space separated parts (allowing for quoted strings)
  - `parts[-1]` = `platinum`
  - `len(document.text)` = 31
  - `gotoparent` - the position where we need to trigger going up to a parent node.



# Backspacing


`set bronze silver gold p parts-1=p len(text)=24 gotoparent=22`

Once we hit 22 we know to call ._parent


# TODO

- What happens if we do <CTRL>+C
