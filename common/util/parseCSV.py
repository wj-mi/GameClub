# coding: utf-8

"""
将CSV文件生成列表格式或者字典格式
根据策划配置的文件，第一行为策划中文注释，第二行为英文key, 其余为数据
"""
import csv

def csv2tuple(filename):
	"""csv2tuple会去除注释和key，只保留数据
	"""
	csvfile = open(filename, 'rb')
	reader = csv.reader(csvfile)
	reader.next() ; reader.next()
	data = [ row for row in reader ]
	return data



if __name__ == "__main__":
	print csv2tuple("Prop.csv")


