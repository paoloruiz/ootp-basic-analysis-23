class CsvWriter:
    def __init__(self):
        self.col_num = 15
        self.csv = ""
    
    def record(self, arr):
        if self.csv == "" and self.col_num < len(arr):
            self.col_num = len(arr)
        while len(arr) < self.col_num:
            arr.append("")
        arr2 = map(lambda a: f"{a:.10f}" if isinstance(a, float) else str(a), arr)
        self.csv += ",".join(arr2) + "\n"

    def getCSV(self):
        return self.csv
        