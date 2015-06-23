import xlrd
import sys
import models

# Delete all word-separating characters, make lowercase and write organization
# with a z.
def clean_string(string):
    return ''.join(string.lower().replace('_', '').replace('-', '').replace('organis', 'organiz').split())

def find_top_row(worksheet):
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1
    while curr_row < num_rows:
        curr_row += 1
        row = worksheet.row(curr_row)
        values = []
        curr_cell = -1
        # Get all the text values into an array.
        # Remove any word-separating characters.
        while curr_cell < num_cells:
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank.
            curr_cell += 1
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            if cell_type == 1:
                cell_value = worksheet.cell_value(curr_row, curr_cell)
                # Be forgiving in terms of word seperators.
                value = clean_string(cell_value)
                values.append(value)
        expected_values = ['organization', 'stakeholdergroup', 'contactperson1', 'contactperson2', 'emailaddress1', 'emailaddress2']
        is_top = True
        for ev in expected_values:
            if ev not in values:
                is_top = False
                break
        if is_top:
            return curr_row
    return -1

def get_cols(worksheet, top_row):
    num_cells = worksheet.ncols - 1
    curr_cell = -1
    columns = [None, None, None, None, None, None]
    column_names = ['organization', 'stakeholdergroup', 'contactperson1', 'emailaddress1', 'contactperson2', 'emailaddress2']
    while curr_cell < num_cells:
        curr_cell += 1
        cell_type = worksheet.cell_type(top_row, curr_cell)
        if cell_type == 1:
            cell_value = worksheet.cell_value(top_row, curr_cell)
            value = clean_string(cell_value)
            if value in column_names:
                columns[column_names.index(value)] = curr_cell
    return tuple(columns)
            
def parse_file(excelfile):
    #script, filename = sys.argv

    #workbook = xlrd.open_workbook(filename)
    workbook = xlrd.open_workbook(file_contents=excelfile.read())

    # Use first sheet by default.
    worksheet = workbook.sheets()[0]

    # If there's a sheet named 'All Contacts', use that.
    for sheetname in workbook.sheet_names():
        lower = sheetname.lower()
        if 'all' in lower and 'contacts' in lower:
            worksheet = workbook.sheet_by_name(sheetname)
            break

    top_row = find_top_row(worksheet)
    name_col, group_col, cname1_col, email1_col, cname2_col, email2_col = get_cols(worksheet, top_row)

    num_rows = worksheet.nrows - 1
    curr_row = top_row
    prev_name = ''
    members = []
    member = None
    while curr_row < num_rows:
        curr_row += 1
        name = worksheet.cell_value(curr_row, name_col)
        if name.lower() != prev_name.lower():
            if member != None:
                members.append(member)
            #member = {}
            #member['name'] = name
            #member['group'] = worksheet.cell_value(curr_row, group_col)
            #member['contacts'] = []
            member = models.Member()
            member.name = name
            member.group = worksheet.cell_value(curr_row, group_col)
            member.contacts = []

        for tup in [(cname1_col, email1_col), (cname2_col, email2_col)]:
            cname_col, email_col = tup
            if worksheet.cell_type(curr_row, email_col) == 1:
                #contact = {}
                #contact['email'] = worksheet.cell_value(curr_row, email_col)
                contact = models.Contact()
                contact.email = worksheet.cell_value(curr_row, email_col)
                if worksheet.cell_type(curr_row, cname_col) == 1:
                    #contact['name'] = worksheet.cell_value(curr_row, cname_col)
                    contact.name = worksheet.cell_value(curr_row, cname_col)
                member.contacts.append(contact)
        prev_name = name
    if member != None:
        members.append(member)
    return members

if __name__ == '__main__':
    script, filename = sys.argv
    file = open(filename, 'r')
    members = parse_file(file)
