class Filter:
    COUNTRY = ['petropavlovsk', 'kostanay', 'astana']

    def __init__(self):
        self.filter_data = [self.COUNTRY,['30000','40000','50000','60000','70000','80000','90000'],
                            ['40000','50000','60000','70000','80000','90000','140000'],['1','2','3'],['1','2','3','4']]
        self.sqldata = {}


    def url_data(self, cn):
        for i,k in enumerate(cn):
            if(k in self.filter_data[i]):
                self.sqldata[i] = k
            else:
                return False
        return self.sqldata
#        return self.url()
    def url(self):

        url = '/{0[0]}/?search%5Bfilter_float_price%3Afrom%5D={0[1]}&search%5Bfilter_float_price%3Ato%5D={0[2]}&search%5Bfilter_float_number_of_rooms%3Afrom%5D={0[3]}&search%5Bfilter_float_number_of_rooms%3Ato%5D={0[4]}'.format(self.sqldata)
        return url