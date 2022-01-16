
class FilterOrders:
    def filter_data(self, min_price=None, max_price=None, status=None, product_name=None, data=None, isNone=False):
        if isNone:
            return data
        else:
            if data:
                new_list = []
                print('\n')
                for i in data:
                    print(i[2])
                    if min_price: pass
                    if max_price: pass
                    if status: 
                        if i[5] == status:
                            print("{}-{}".format(status, i[5]))
                            new_list.append(i)

                            if product_name: 
                                if i[2] == product_name:
                                    new_list.append(i)
                return new_list
            else:
                return []