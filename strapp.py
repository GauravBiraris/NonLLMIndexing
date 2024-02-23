import streamlit as st
from indexer import Indexer
from catalog import Catalog, Item
from whoosh.writing import BufferedWriter
import os

os.makedirs("indexdir", exist_ok=True)

catalog = Catalog()
indexer = Indexer()

catalog.add_item(Item("Dummy 1", {"Mega haul"}))
catalog.add_item(Item("Dummy 2", {"Intense orange yellow pigment"}))

# writer = BufferedWriter(indexer.index, period=120, limit=20)

st.title('My Catalog App')

# Index catalog
st.write('Indexing catalog...')
writer = BufferedWriter(indexer.index)
try:
  writer.lock()
  indexer.index_catalog(catalog)
  st.write('Done!')
  writer.commit()
finally:
  writer.unlock()


# Add item
st.header('Add New Item')
name = st.text_input('Name')
desc = st.text_area('Description')
if st.button('Add'):
  item = Item(name, desc) 
  writer = BufferedWriter(indexer.index)
  try:
    writer.lock()
    indexer.index_item(item)
    catalog.add_item(item)
    st.success('Item added!')
    writer.commit()
  finally:
    writer.unlock()


# Update item
items = {item.id: item.name for item in catalog.items}
selected_id = st.selectbox('Select item to update', options=items.keys())  
name = st.text_input('New name', value=catalog.get_item(selected_id).name)
desc = st.text_area('New description', value=catalog.get_item(selected_id).desc)
if st.button('Update'):
  item = catalog.get_item(selected_id)
  writer = BufferedWriter(indexer.index)
  if item:
    try:
      name = st.text_input("New name", value=item.name)
      writer.lock()
      item.name = name
      item.desc = desc
      indexer.update_item(item)
      writer.commit()
      st.success('Item updated!')
    finally:
      writer.unlock()
  else:
    st.warning("Item not found")

# Delete item
selected_id = st.selectbox('Select item to delete', options=items.keys())
if st.button('Delete'):
  writer = BufferedWriter(indexer.index)
  try:
    writer.lock() 
    indexer.delete_item(selected_id)
    catalog.delete_item(selected_id)
    writer.commit()
    st.warning('Item deleted!')
  finally:
    writer.unlock()

# Search 
query = st.text_input('Search')  
if query:
  writer = BufferedWriter(indexer.index)
  try:
    writer.lock() 
    writer.commit()
    results = indexer.search(query)
    for rank, item in enumerate(results):
      st.write(f'{rank+1}. {item.name} ({item.id})')
  finally:
    writer.unlock()
