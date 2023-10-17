class DoIt:
    # constructor
    def __init__(self, filename):
        print("!")
        self.filename = filename
        self.raw_data = []
        with open(self.filename, 'r') as f:
            for line in f:
                self.raw_data.append(self.expand(line.strip().split(',')))
        

    def expand(self, listin):
        threadname: str = listin[0]
        processedin = listin[1:]
        processedin1 = [int(x) for x in processedin]
        listout = []
        listout.extend("-"*processedin1[0])
        listout.extend("c"*processedin1[1])
        listout.extend("i"*processedin1[2])
        listout.extend("c"*processedin1[3])
        listout.extend("i"*processedin1[4])
        listout.extend("c"*processedin1[5])
        return listout



if __name__ == '__main__':
    d = DoIt('data1.csv')
    # d.expand(d.raw_data[0])
    print(d.raw_data)

