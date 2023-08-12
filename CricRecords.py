import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import numpy as np
import base64
import lxml

basic_url = 'https://www.espncricinfo.com/records'

def get_doc(basic_url):
    re = requests.get(basic_url,'html.parser')
    doc = bs(re.content)
    doc.prettify()
    return doc

doc = get_doc(basic_url)
a_link_class = 'ds-cursor-pointer ds-inline-flex ds-items-center ds-w-full ds-py-2 ds-text-tight-s ds-px-4 ds-bg-ui-fill ds-text-typo ds-flex ds-items-center ds-box-border hover:ds-bg-ui-fill-hover active:ds-bg-ui-fill-primary active:ds-text-raw-white focus:ds-border focus:ds-border-ui-stroke-primary focus:ds-outline-none ds-pl-8'

def get_format_links(doc):
    test_record_links = []
    odi_record_links = []
    t20_record_links =[]
    base_url = 'https://www.espncricinfo.com'
    div_tags_format = doc.find_all('div',{'class':'ds-w-full ds-bg-fill-content-prime ds-overflow-hidden ds-rounded-xl ds-border ds-border-line'})
    for i in range(len(div_tags_format)):
        z = div_tags_format[i].find_all('a')
        for j in range(len(z)):
            t =z[j]['href']
            if i == 0 and j not in [1,8]:
                test_record_links.append(base_url + t)
            if i == 1 and j not in [1,8]:
                odi_record_links.append(base_url+t)
            if i == 2 and j not in [1,8]:
                t20_record_links.append(base_url+t)
    
    return test_record_links,odi_record_links,t20_record_links

test_rec , odi_rec , t20_rec = map(list,get_format_links(doc))

def get_format_doc(format_rec):
    format_doc = bs(requests.get(format_rec[0]).content,'html.parser')
    return format_doc

def all_cat(format_rec):
    format_doc = bs(requests.get(format_rec[0]).content,'html.parser')
    all_cat = format_doc.find_all('span',{'class':'ds-text-title-subtle-m ds-font-medium ds-text-typo hover:ds-text-typo-primary ds-block'})
    all_cat =[i.get_text() for i in all_cat][1:-1]
    return all_cat


def get_selected(format_doc):
    user_test = format_doc.find_all('div',{'class':'ds-w-full ds-bg-fill-content-prime ds-overflow-hidden ds-rounded-xl ds-border ds-border-line ds-mb-2'})[1:-2]
    base_url = 'https://www.espncricinfo.com'
    tags_cat_list = []
    tags_cat_links = []

    for i in user_test:
        q = i.find_all('a',{'class':a_link_class})
        select_cat = []
        select_cat_link = []
        for t in q:
            select_cat.append(t.get_text())
            select_cat_link.append(base_url+t['href'])
        tags_cat_links.append(select_cat_link)
        tags_cat_list.append(select_cat)
    
    return tags_cat_list, tags_cat_links 

def get_allData_page(url):
    r = requests.get(url)
    c = r.content
    subCat_doc = pd.read_html(c)
    df = pd.DataFrame(subCat_doc[0])
    if df.size == 1:
        return "No Records Found"
    for i in range(1,len(subCat_doc)):
        t = pd.DataFrame(subCat_doc[i])
        df = pd.concat([df,t],ignore_index=True)
        
    return df

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.title("CricRecords")
st.image('cricket.jpg')
st.caption('Credits : Unsplash ')

one = st.container()

st.markdown('''
        <style>
        .main{
        background-color: #e5eaf5
        }
        
        div.css-1v0mbdj.e115fcil1 {
          width: 100%;
          padding: 10px;
          border: 1px solid #ccc;
          border-radius: 5px;
          background-color: #fff;
          margin-bottom: 10px;
        }
        
        div.st-ae.st-af.st-ag.st-bc.st-ai.st-aj.st-bd.st-be.st-b8
        {
          width: 100%;
          padding: 10px;
          border: 1px solid #ccc;
          border-radius: 5px;
          background-color: #fff;
          margin-bottom: 10px;
        }
        
        </style>''',
            unsafe_allow_html=True
            )

with st.sidebar:
    st.markdown('### Choose Format of Record')
    formats = ['Test Cricket','ODI Internationals','T20 Internationals']
    selected_form = st.selectbox('Select Your Choice of format',formats)
    if selected_form == 'Test Cricket':
        selected_form_rec = test_rec
        all_cat = all_cat(test_rec)
    elif selected_form == 'ODI Internationals':
        selected_form_rec = odi_rec
        all_cat = all_cat(odi_rec)
    else:
        selected_form_rec = t20_rec
        all_cat = all_cat(t20_rec)
    format_doc = get_format_doc(selected_form_rec)
    all_sub_cat = get_selected(format_doc)
    st.markdown('### Choose the category of your choice')
    selected_cat = st.selectbox('Select your choice of Category', all_cat)

with one:
    st.write('Introducing CricRecords: Your go-to for cricket data by format and record type. Easily view and download comprehensive information. Explore cricket like never before!.')
    st.markdown('## Steps to find your favourite record data ')
    st.markdown(' 1. Choose your choice of format in the sidebar \n  2. Select your Category type in the sidebar menu \n 3. Choose your record type from the menu below \n - **Note : Please wait momentarily if your requested record is being fetched.**')
    
    selected_cat_index = all_cat.index(selected_cat)
    st.markdown('### Select your choice of record you want to see from the following dropdown menu')
    selected_subcat = st.selectbox('Select Your Choice of Record',all_sub_cat[0][selected_cat_index])
    selected_subcat_index = all_sub_cat[0][selected_cat_index].index(selected_subcat)                                                                
    df = get_allData_page(all_sub_cat[1][selected_cat_index][selected_subcat_index])
    
    st.dataframe(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

    
    
    
