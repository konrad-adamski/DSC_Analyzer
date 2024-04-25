import pandas as pd
import xlsxwriter


# add to excel-------------------------------------------------------------------------------
def add_to_excel(dframe_in, writer, my_sheet_name="1", with_index=False):
    dframe = dframe_in.copy()

    if with_index:
        dframe.reset_index(inplace=True)

    # add new worksheet
    dframe.to_excel(writer, sheet_name=my_sheet_name, startrow=0, index=False)
    worksheet = writer.sheets[my_sheet_name]

    # set column width
    for c in dframe.columns:
        col_index = dframe.columns.get_loc(c)
        col_max_len = ((dframe[c].astype(str).str.len()).max())
        col_max_len = max(len(c) + 4, col_max_len)

        if col_max_len > 30:
            col_max_len = 30

        worksheet.set_column(col_index, col_index, col_max_len)

    # set as table
    worksheet = set_as_table(dframe, worksheet)

    return worksheet


# set as table--------------------------

def set_as_table(dframe, my_worksheet):
    column_settings = [{'header': column} for column in dframe.columns]
    (max_row, max_col) = dframe.shape
    min_row = 0
    min_col = 0
    max_row = max_row

    my_worksheet.add_table(min_row, min_col, max_row, max_col - 1, {'total_row': False, 'columns': column_settings})

    return my_worksheet
