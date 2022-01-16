import csv as cv
from io import StringIO
import pyexcel as pe


class CsvReport:
    def gen_report(self, data:list, filtered:bool):
        csv_data = [ [ "Date ordered", "Deliver by date", "Product", "Quantity", "Cost", "status", "Restaurant"] ]
        
        if filtered:
            for item in data:
                temp = [
                        item[0].strftime("%b-%d-%Y"), item[1].strftime("%b-%d-%Y"), item[2], item[3], item[4], item[5], item[6]
                ]
                csv_data.append(temp)
                    
        else:
            for item in data:
                temp = [   item.Orders.date_ordered.strftime("%b-%d-%Y"), item.deliver_by_date.strftime("%b-%d-%Y"),
                        item.product.product_name, item.quantity, item.price, item.status, item.Orders.restuarant.name
                    ]
                csv_data.append(temp)

        si = StringIO()
        sheet = pe.Sheet(csv_data)
        sheet.save_to_memory("csv", si)
        
        return si.getvalue()



# r = CsvReport()

# print(r.gen_report([], True))

