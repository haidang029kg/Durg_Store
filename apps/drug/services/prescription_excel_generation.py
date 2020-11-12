from datetime import datetime

import xlsxwriter

from apps.drug.models import Prescription, PrescriptionDetail


class PrescriptionExcelGeneration:

    def __init__(self, prescription_id: str):
        self.__prescription = Prescription.objects.get(id=prescription_id)
        assert self.__prescription.pharmacy.email is not None, "Pharmacy email is not None"
        self.__data = PrescriptionDetail.objects.filter(prescription=self.__prescription)
        self.__path = './file_bucket/{}-{}.xlsx'.format(self.__prescription.pharmacy.name,
                                                   datetime.now().date())

    def xlsx(self):
        workbook = xlsxwriter.Workbook(self.__path)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, 'STT')
        worksheet.write(0, 1, 'Tên')
        worksheet.write(0, 2, 'Có hàng')
        worksheet.write(0, 3, 'Giá đơn vị')
        worksheet.write(0, 4, 'Số lượng')
        worksheet.write(0, 5, 'Tổng giá')
        for index_row, row in enumerate(self.__data):
            worksheet.write(index_row + 1, 0, index_row + 1)
            worksheet.write(index_row + 1, 1, row.drug.name)
            worksheet.write(index_row + 1, 2, row.is_available)
            worksheet.write(index_row + 1, 3, row.price_at_the_time)
            worksheet.write(index_row + 1, 4, row.quantity)
            worksheet.write(index_row + 1, 5, '= D{} * E{}'.format(index_row + 2, index_row + 2))

        worksheet.write(len(self.__data) + 2, 4, 'Total')
        worksheet.write(len(self.__data) + 2, 5, '=SUM(F2:F{})'.format(len(self.__data) + 1))

        workbook.close()

    def exec(self):
        self.xlsx()
