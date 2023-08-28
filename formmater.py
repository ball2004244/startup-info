import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Tuple

#* Format index.html to data.csv
# in_file = 'index.html'
# out_file = 'data.csv'

print('Start formmating...')
def get_data_table(in_file: str) -> BeautifulSoup:
    with open(in_file, 'r') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', {'class': 'headerAndDataRowContainer'})

    return table

def process_left_pane(table: BeautifulSoup) -> Tuple[str, List[str]]:
    # get all rows in the first column
    first_col = table.find('div', {'class': 'leftPaneWrapper'})
    header = first_col.find('div', {'class': ['headerLeftPane', 'pane']})
    
    # get content of the header
    header_content = header.find('span', {'class': 'name'}).find('div').find('div').text
    
    # get content of the table body
    data = first_col.find('div', {'class': 'dataLeftPane'})
    rows: List[BeautifulSoup] = data.find_all('div', {'class': ['dataRow', 'leftPane']})
            
    processed_data = []
    for row in rows:
        datum = row.find('div', {'data-rowindex': True})
        if datum is None:
            continue
        
        row_content = datum.find('div').find('div').text
        
        processed_data.append(row_content)
    
    return header_content, processed_data
                
def process_right_pane(table: BeautifulSoup) -> Tuple[List[str], List[List[str]]]:
    rest_cols = table.find('div', {'class': 'rightPaneWrapper'})
    headers = rest_cols.find('div', {'class': ['headerRightPane', 'pane']})
        
    # process headers
    headers = headers.find_all('div', {'data-columnindex': True})
    header_contents = []

    for header in headers:
        header_content = header.find('span', {'class': 'name'}).find('div').find('div').text

        header_contents.append(header_content)

    # process table body
    data = rest_cols.find('div', {'class': 'dataRightPane'})
    rows: List[BeautifulSoup] = data.find_all('div', {'class': ['dataRow', 'rightPane']})
    
    processed_data = []
    for row in rows:
        datum: List[BeautifulSoup] = row.find_all('div', {'data-columnindex': True})
        # get col_index from datum
        col_index = datum[0]['data-columnindex']
        
        company_info = []
        for cell in datum:
            processed_cell = cell.find('div')
            
            if processed_cell is None:
                cell_content = ''
            elif col_index == '6':
                cell_content = processed_cell.find('span').text
            else:
                cell_content = processed_cell.text
            
            company_info.append(cell_content)
            
        processed_data.append(company_info)
            
    return header_contents, processed_data

def construct_csv() -> None:
    left_header, left_data = process_left_pane(table)
    right_headers, right_data = process_right_pane(table)
    
    # convert left and right to pandas dataframe
    left_df = pd.DataFrame(left_data, columns=[left_header])
    right_df = pd.DataFrame(right_data, columns=right_headers)
    
    # merge left and right dataframe
    df = pd.concat([left_df, right_df], axis=1)
    
    # save to csv
    df.to_csv(out_file, index=False)

def formatter() -> None:
    import os
    from logic import first_diff_idx
    folder = 'temp'
    num_files = len(os.listdir(folder))
    
    final_file = 'final.txt'
    if os.path.exists(final_file):
        # overwrite final.txt with blank
        with open(final_file, 'w') as f:
            f.write('')
    i = 1
    while i < num_files:
        j = i - 1
        
        # read file i and j
        table_i = get_data_table('%s/index_%d.html' % (folder, i))
        table_j = get_data_table('%s/index_%d.html' % (folder, j))
        
        # process table_i and table_j
        left_header_i, left_data_i = process_left_pane(table_i)
        left_header_j, left_data_j = process_left_pane(table_j)
        
        # find index of first different element in left_data_i and left_data_j
        
        idx = first_diff_idx(left_data_j, left_data_i)
        
        # if 2 lists are the same, do nothing
        if idx == -1:
            i += 1
            continue
        
        # otherwise, move the cursor to the idx-th element
        left_data = left_data_i[idx:]
        
        # store to final.txt
        with open(final_file, 'a') as f:
            # add iteration
            f.write('Iteration %d\n' % i)
            # write left_data with , as delimiter
            f.write(','.join(left_data))
            f.write('\n')
        i += 1
        
formatter()

print('Done formmating!')
