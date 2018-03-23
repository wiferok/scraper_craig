# simple script to check data

"""Check if column x is empty or exist
if exist"""

"""
search if the column y contain string 'XxxX'
"""
from scrapy.utils.project import get_project_settings
import pandas as pd


def check(search_s,value, not_value, column_name, df=None):

    counter = 0
    counter_pos = 0

    for row in df.iterrows():
        counter+=1
        if search_s.lower() in df.loc[row[0], 'Description'].lower(): # row[0] contains id value
            counter_pos+=1
            df.loc[row[0], column_name] = value
        else:
            df.loc[row[0], column_name] = not_value

    print('INFO STATS FOR COLUMN -"%s":'%column_name)
    print('\tROWS CHECKED: %s'%counter)
    print('\t- VALUES <<"%s">> added: %s'%(value, counter_pos))
    print('\t- VALUES <<"%s">> added: %s'%(not_value, counter - counter_pos))
    return df

def main(combos):
    """function to perform searches for each combo"""
    setts = get_project_settings()
    print('Loading...\n\n')
    df = pd.read_csv(setts['CSV_FILEPATH'],
                     index_col='Craiglist_PostingID',
                     encoding='UTF-8'
                     )
    columns_list = combos.search_combos.items()

    for column in columns_list:

        column_name = column[0]
        column_values = column[1]

        df = check(
                search_s= column_values['search_s'],
                value = column_values['value'],
                not_value = column_values['not_value'],
                column_name = column_name,
                df=df
            )
        print('='*10)

    print('Do you want to save results?')

    if input('Y/N?\n').lower() == 'y':
        df.to_csv('output.csv', encoding='UTF-8')
        print('output.csv saved')

    print('Exiting..')


class Search_combos():
    """ Class to make adding new search_combos with a small interface"""

    def __init__(self):
        self.search_combos = {}

    def add_combo(self, search_s, value, not_value, column_name):
        self.search_combos.update(
            {
            column_name:
                dict(
                    value=value,
                    not_value=not_value,
                    search_s=search_s,
                )
            }
        )


if __name__ == '__main__':
    combos = Search_combos()

    ### FROM HERE YOU CAN ADD FEW SEARCH COMBOS ###

    combos.add_combo(
        search_s='granite',
        value = 'Y',
        not_value = 'N',
        column_name = 'Granite countergroup'
    )

    combos.add_combo(
        search_s='phone',
        value = 'phone number exist',
        not_value = 'no phone number',
        column_name= 'Phone Numbers'
    )

    ### TILL HERE ###

    main(combos)



