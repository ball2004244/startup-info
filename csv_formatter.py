import os
import pickle
import pandas as pd
from typing import List, Tuple
from bs4 import BeautifulSoup

'''
    This script is used to format the scraped data to csv file
'''

# * Get data from scraped file
# * Input: html filepath
# * Output: BeautifulSoup object of the table


def get_data_table(in_file: str) -> BeautifulSoup:
    with open(in_file, 'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', {'class': 'headerAndDataRowContainer'})

    return table

# * Process the left side of the table
# * Input: BeautifulSoup object of the table
# * Output: header and data of the left pane


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

# * Process the right side of the table
# * Input: BeautifulSoup object of the table
# * Output: header and data of the right pane


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

# * Merge left and right data
# * Input: left header, left data, right headers, right data
# * Output: merged data


def process_data(table: BeautifulSoup) -> pd.DataFrame:
    left_header, left_data = process_left_pane(table)
    right_headers, right_data = process_right_pane(table)

    left_df = pd.DataFrame(left_data, columns=[left_header])
    right_df = pd.DataFrame(right_data, columns=right_headers)

    merged_df = pd.concat([left_df, right_df], axis=1)

    return merged_df

# * Format and save data to csv file
# * Input:
# *   out_file: path to output csv file (Optional)
# *   folder: path to folder containing scraped html files (Optional)
# * Output: None
# * Note: check_set.pkl is a set to keep track of
# *       all companies added to csv, to prevent duplicates


def formatter(out_file: str = 'final.csv', folder: str = 'temp', check_file: str = 'check_set.pkl') -> None:
    # create output file if it doesn't exist
    if not os.path.exists(out_file):
        with open(out_file, 'w') as f:
            f.write('')

    # create check_set file if it doesn't exist
    if not os.path.exists(check_file):
        with open(check_file, 'wb') as f:
            pickle.dump(set(), f)

    # load check_set
    with open(check_file, 'rb') as f:
        check_set = pickle.load(f)

    # loop through all html files and add new data to csv
    for i, filename in enumerate(os.listdir(folder)):
        cur_file = os.path.join(folder, filename)
        table = get_data_table(cur_file)
        merged_df = process_data(table)

        temp_data = merged_df.iloc[:, 0]
        # loop through first column and check if data is in check_set
        for j, datum in enumerate(temp_data):
            if datum not in check_set:
                check_set.add(datum)
            else:
                # remove data position j from merged_df
                merged_df.drop(j, inplace=True)

        # only save when merged_df is not empty
        if merged_df.empty:
            continue

        # add header to csv
        if os.path.getsize(out_file) == 0:
            merged_df[:0].to_csv(out_file, mode='w', index=False)

        # add data to csv
        merged_df.to_csv(out_file, mode='a', header=False, index=False)

        # save check_set to check_set.pkl
        with open(check_file, 'wb') as f:
            pickle.dump(check_set, f)


if __name__ == '__main__':
    print('Start formatting...')
    csv_file = 'final.csv'
    formatter(csv_file)
    print('Done formatting!')
