import os
import pickle
import pandas as pd
from typing import List, Tuple
from bs4 import BeautifulSoup

# * Format html file to csv


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
    header_content = header.find(
        'span', {'class': 'name'}).find('div').find('div').text

    # get content of the table body
    data = first_col.find('div', {'class': 'dataLeftPane'})
    rows: List[BeautifulSoup] = data.find_all(
        'div', {'class': ['dataRow', 'leftPane']})

    processed_data = []
    for row in rows:
        datum = row.find('div', {'data-rowindex': True})
        if datum is None or datum.find('div') is None or datum.find('div').find('div') is None:
            row_content = ''
        else:
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
        header_content = header.find(
            'span', {'class': 'name'}).find('div').find('div').text

        header_contents.append(header_content)

    # process table body
    data = rest_cols.find('div', {'class': 'dataRightPane'})
    rows: List[BeautifulSoup] = data.find_all(
        'div', {'class': ['dataRow', 'rightPane']})

    processed_data = []
    for row in rows:
        datum: List[BeautifulSoup] = row.find_all(
            'div', {'data-columnindex': True})
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

        # check if len of company_info is 6, if not, add empty string at beginning
        while len(company_info) < 6:
            company_info.insert(0, '')
            
        processed_data.append(company_info)

    return header_contents, processed_data


def formatter() -> None:
    try:
        folder = 'temp'
        out_file = 'final.csv'
        num_files = len(os.listdir(folder))
        add_header = True

        for i in range(num_files):
            # get prev_set
            prev_file = 'prev_set.pkl'
            # verify if prev_set.pkl exists with os

            if os.path.exists(prev_file):
                with open(prev_file, 'rb') as f:
                    prev_set = pickle.load(f)
            else:
                prev_set = set()

            cur_file = '%s/index_%d.html' % (folder, i)
            table = get_data_table(cur_file)
            left_header, left_data = process_left_pane(table)
            right_headers, right_data = process_right_pane(table)
            
            left_df = pd.DataFrame(left_data, columns=[left_header])
            right_df = pd.DataFrame(right_data, columns=right_headers)

            # loop through data and add to prev_set
            for j, datum in enumerate(left_data):
                if datum not in prev_set:
                    prev_set.add(datum)
                else:
                    # remove data position j from left_df and right_df
                    left_df.drop(j, inplace=True)
                    right_df.drop(j, inplace=True)

            # merge left_df and right_df
            merged_df = pd.concat([left_df, right_df], axis=1)

            # only save when merged_df is not empty
            if merged_df.empty:
                continue

            # add header if necessary
            # if add_header:
            #     merged_header = [left_header] + right_headers
            #     merged_header_df = pd.DataFrame([merged_header])
            #     merged_header_df.to_csv(out_file, mode='w', header=False, index=False)
            #     add_header = False

            # # add merged data to csv
            merged_df.to_csv(out_file, mode='a', header=False, index=False)

            # save prev_set to prev_set.pkl
            with open(prev_file, 'wb') as f:
                pickle.dump(prev_set, f)
    except Exception as e:
        # locate line of error
        import sys
        
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        
        print('Error at line %d' % exc_tb.tb_lineno)
        print(e)
        print('Exiting...')
