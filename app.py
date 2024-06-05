import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

def parse_xml(xml_file):
    namespaces = []
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for namespace in root.findall('.//{http://www.developer.cognos.com/schemas/bmt/60/12}namespace'):
        namespace_info = {}
        try:
            namespace_info['name'] = namespace.find('{http://www.developer.cognos.com/schemas/bmt/60/12}name').text
        except AttributeError:
            namespace_info['name'] = "N/A"
        try:
            namespace_info['lastChanged'] = namespace.find('{http://www.developer.cognos.com/schemas/bmt/60/12}lastChanged').text
        except AttributeError:
            namespace_info['lastChanged'] = "N/A"
        try:
            namespace_info['lastChangedBy'] = namespace.find('{http://www.developer.cognos.com/schemas/bmt/60/12}lastChangedBy').text
        except AttributeError:
            namespace_info['lastChangedBy'] = "N/A"

        # Fetch folder details
        folder_details = []
        for folder in namespace.findall('.//{http://www.developer.cognos.com/schemas/bmt/60/12}folder'):
            folder_info = {}
            try:
                folder_info['name'] = folder.find('{http://www.developer.cognos.com/schemas/bmt/60/12}name').text
            except AttributeError:
                folder_info['name'] = "N/A"
            try:
                folder_info['description'] = folder.find('{http://www.developer.cognos.com/schemas/bmt/60/12}description').text or "No description available"
            except AttributeError:
                folder_info['description'] = "N/A"
            try:
                folder_info['lastChanged'] = folder.find('{http://www.developer.cognos.com/schemas/bmt/60/12}lastChanged').text
            except AttributeError:
                folder_info['lastChanged'] = "N/A"
            try:
                folder_info['lastChangedBy'] = folder.find('{http://www.developer.cognos.com/schemas/bmt/60/12}lastChangedBy').text
            except AttributeError:
                folder_info['lastChangedBy'] = "N/A"
            folder_details.append(folder_info)
        namespace_info['folders'] = folder_details

        # Fetch query details
        query_details = []
        for query in namespace.findall('.//{http://www.developer.cognos.com/schemas/bmt/60/12}querySubject'):
            query_info = {}
            try:
                query_info['name'] = query.find('{http://www.developer.cognos.com/schemas/bmt/60/12}name').text
            except AttributeError:
                query_info['name'] = "N/A"
            try:
                query_info['description'] = query.find('{http://www.developer.cognos.com/schemas/bmt/60/12}description').text or "No description available"
            except AttributeError:
                query_info['description'] = "N/A"
            
            # Fetch SQL query
            try:
                query_info['sql'] = query.find('.//{http://www.developer.cognos.com/schemas/bmt/60/12}dbQuery/{http://www.developer.cognos.com/schemas/bmt/60/12}sql').text
            except AttributeError:
                query_info['sql'] = "N/A"

            # Fetch query item details
            query_items = query.findall('.//{http://www.developer.cognos.com/schemas/bmt/60/12}queryItem')
            query_item_info = []
            for query_item in query_items:
                item_info = {}
                try:
                    item_info['name'] = query_item.find('{http://www.developer.cognos.com/schemas/bmt/60/12}name').text
                except AttributeError:
                    item_info['name'] = "N/A"
                try:
                    item_info['description'] = query_item.find('{http://www.developer.cognos.com/schemas/bmt/60/12}description').text or "No description available"
                except AttributeError:
                    item_info['description'] = "N/A"
                try:
                    item_info['externalName'] = query_item.find('{http://www.developer.cognos.com/schemas/bmt/60/12}externalName').text
                except AttributeError:
                    item_info['externalName'] = "N/A"
                try:
                    item_info['dataType'] = query_item.find('{http://www.developer.cognos.com/schemas/bmt/60/12}datatype').text
                except AttributeError:
                    item_info['dataType'] = "N/A"
                query_item_info.append(item_info)
            query_info['queryItems'] = query_item_info

            query_details.append(query_info)
        namespace_info['queries'] = query_details

        namespaces.append(namespace_info)

    return namespaces

def main():
    st.title("Package Manager Metadata Extractor")
    
    xml_file = st.file_uploader("Upload XML file", type=["xml"])
    if xml_file is not None:
        namespaces = parse_xml(xml_file)
        tabs = ["Namespace", "Data Sources"]
        selected_tab = st.sidebar.selectbox("Select Tab", tabs)

        if selected_tab == "Namespace":
            if namespaces:
                for index, namespace in enumerate(namespaces, start=1):
                    st.write(f"## Namespace {index}:")
                    st.write(f"Name: {namespace['name']}")
                    st.write(f"Last Changed: {namespace['lastChanged']}")
                    st.write(f"Last Changed By: {namespace['lastChangedBy']}")
                    st.write("---")

                    st.write("### Folder Details:")
                    folder_df = pd.DataFrame(namespace['folders'])
                    st.write(folder_df)

                    st.write("### Query Details:")
                    for query in namespace['queries']:
                        st.write(f"- Name: {query['name']}")
                        st.write(f"  Description: {query['description']}")
                        st.write(f"  SQL: {query['sql']}")
                        st.write("  Query Items:")
                        query_item_df = pd.DataFrame(query['queryItems'])
                        st.write(query_item_df)
                    st.write("---")

        elif selected_tab == "Data Sources":
            data_sources = []
            for namespace in namespaces:
                for ds in namespace.get("datasources", []):
                    data_sources.append(ds)
            if data_sources:
                data_sources_df = pd.DataFrame(data_sources)
                st.write("## Data Sources")
                st.write(data_sources_df)
            else:
                st.write("No data sources found.")

if __name__ == "__main__":
    main()