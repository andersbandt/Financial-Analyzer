
# import needed modules
import gui
import db

# main: main function of the program. Really just calls gui_driver
def main():
    gui.main()

def db_init():
    """Create the database using the values of TableStatements. """
    from db import TableStatements, DATABASE_DIRECTORY, all_tables_init    
    statements = []
    for value in TableStatements.__dict__.values():
        if str(value).startswith('CREATE'): # Only append the values of the variables. Without this we would get the built-ins and the docstring.
            statements.append(value)
    all_tables_init(statements, DATABASE_DIRECTORY)

# thing that's gotta be here
if __name__ == "__main__":
    # db_init() # only used if database doesn't exist
    main()






