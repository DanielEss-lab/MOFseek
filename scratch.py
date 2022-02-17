if __name__ == '__main__':
    txt = "O`=C([O`-])C1=CC=C(C([O`-])=O`)C=C1"
    e = 'O'
    x = txt.replace(e + '`', e)

    print(x)
