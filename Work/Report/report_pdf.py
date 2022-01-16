from fpdf import FPDF

from flask import session

pdf = FPDF(orientation='L', unit='mm', format='letter')
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font(family="helvetica",style="", size=12 )


table_headers = ['Date ordered', 'Deliver by date', 'Product', 'Quantity', 'Cost(R)', ' Status', 'Restuarant']


GRAY=[216, 230, 235]
WHITE=[255, 255, 255]



class PDF(FPDF):
    # def header(self):
    #     return super().header()

    def __init__(self, orientation="portrait", unit="mm", format="A4", font_cache_dir=True):
        super().__init__(orientation=orientation, unit=unit, format=format, font_cache_dir=font_cache_dir)
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font(family="helvetica",style="", size=12 )

        self.table_header = ['Date Ordered', 'Deliver by date', 'Product', 'Quantity', 'Cost', 'Status', 'Restaurant']

    def generate_pdf(self, db_data):
        data = self._filter_data(db_data)

        counter = 0
        
        self._add_table_header()

        self.set_font_size(12)
        for d in data:
        
            # changing color of each row in a table, for better visiblity 
            if counter % 2 == 0:
                self.set_fill_color(*GRAY)
            else:
                self.set_fill_color(*WHITE)


            for j, i in enumerate(d):
                # writing each column value to the table row

                if j == 6:
                    # adding a wider width for retuarant column t fit resturant name  
                    self.cell(w=50, h=10, txt = str(i), border=1, fill=True)
                else:
                    self.cell(w=30, h=10, txt = str(i), border=1, fill=True)

            # moving to new line after writing each column
            self.ln(h=10)

            counter += 1
        return self.output(dest="S")

    def _filter_data(self, db_data):
        data = []
        
        # anyFilter: to check if the user appied any filters to the orders data before they try to download the pdf
        
        if not session.get('dataAvailable'):
            
            for item in db_data:
                data.append(
                    [   item.Orders.date_ordered.strftime("%b-%d-%Y"), item.deliver_by_date.strftime("%b-%d-%Y"),
                        item.product.product_name, item.quantity, item.price, item.status, item.Orders.restuarant.name
                    ]
                )
        else:
            for item in db_data:
                
                data.append(
                    [
                        item[0].strftime("%b-%d-%Y"), item[1].strftime("%b-%d-%Y"), item[2], item[3], item[4], item[5], item[6]
                    ]
                )
        return data

    def _add_table_header(self,):

        self.set_fill_color(*WHITE)

        # This will add the table header or column names before adding the order data 
        for j, i in enumerate(self.table_header):

            if j == 6:
                self.cell(w=50, h=10, txt = str(i), border=1, fill=True)
            else:
                self.cell(w=30, h=10, txt = str(i), border=1, fill=True)

        self.ln(h=10)

# global counter = 0

# def generate_pdf(id):
#     data = [table_headers]
    
#     order = OrderItems.query.filter_by(farmer_id=id)
#     for item in order:
#         data.append(
#             [   item.Orders.date_ordered.strftime("%b-%d-%Y"), item.deliver_by_date.strftime("%b-%d-%Y"),
#                 item.product.product_name, item.quantity, item.price, item.status, item.Orders.restuarant.name
#             ]
#         )
#     counter = 0
#     for d in data:

#         # changing color of each row in a table, for better visiblity 
#         if counter % 2 == 0:
#             pdf.set_fill_color(*GRAY)
#         else:
#             pdf.set_fill_color(*WHITE)


#         for j, i in enumerate(d):
#             # writing each column value to the table row

#             if j == 6:
#                 # adding a wider with for retuarant column t fit resturant name  
#                 pdf.cell(w=50, h=10, txt = str(i), border=1, fill=True)
#             else:
#                 pdf.cell(w=30, h=10, txt = str(i), border=1, fill=True)

#         # moving to new line after writing each column
#         pdf.ln(h=10)

#         counter += 1
    
#     pdf.output("test.pdf")



