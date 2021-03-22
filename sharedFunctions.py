from configparser import ConfigParser

#This function was taken out of guiFunctions section to prevent a import reference cycle between guiFunctions and sqlFunctions

def iniFileParser(fileName, section):
    
    parser = ConfigParser()
    parser.read(fileName)

    db={}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(PGsection, fileName))

    return db
