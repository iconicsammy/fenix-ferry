from prettytable import PrettyTable
def dbRowsToDict(cursor):
    '''
    cursor.fetchall() returns tuples. Convert those to dictionaries
    '''
    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return {'columns': columns,'rows': rows}

def showDirections(directions, test_mode = False):
    '''
    Print directions to the screen.
    @input directions: an array of directions to print
    '''
    if not test_mode:
        for direction in directions:
            print(direction)

def drawTable(field_names, records, title, test_mode = False):
    '''
    Given records, draw table
    @input cursor: cursor object
    @input records: an array of records retrieved by the cursor
    '''
    if not test_mode:
        lines = '*' * 50
        print(lines)
        print(' ' + title)
        print(lines)
        x = PrettyTable()
        x.field_names = field_names
        for row in records:
            rows =[]
            for field in field_names:
                rows.append(row[field])
            x.add_row(rows)
        
        print(x)
        # add empty line
        print(' ')