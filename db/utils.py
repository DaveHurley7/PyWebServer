PK = "primary key"

def create_table(table,*col_info):
    cols = ""
    for col in col_info:
        cols += col_info[0] + " " + col_info[1]
        if col_info[1] == "varchar":
            cols += "("+col_info[2]+") "
        else:
            cols += " "
        if len(col_info) > 2 and col_info[1] != "varchar":
            pass

