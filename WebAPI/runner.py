#a simple runner for test purposes

from mnemoapi import MnemoWebAPI

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../')
    from persistance import basedatabase
    m = MnemoWebAPI(basedatabase.BaseDatabase('sqlite:///../test.db'))
