# OpenZoo Fonts Builder - mapping tables

import copy

class MappingTable:
	def __init__(self, table=None):
		self.__map = {}
		if table is not None:
			for i in range(len(table)):
				self.put(i, table[i])
	
	def get(self, key):
		if key not in self.__map:
			return None
		else:
			return self.__map[key]

	def put(self, key, value):
		if key not in self.__map:
			self.__map[key] = []
		if type(value) is list:
			self.__map[key] += value
		else:
			self.__map[key].append(value)
	
	def remove(self, key, value=None):
		if value is None:
			self.__map.pop(key, None)
		else:
			while value in self.__map[key]:
				self.__map[key].remove(value)
			if len(self.__map[key]) <= 0:
				self.__map.pop(key, None)

	def remap(self, keys=None, values=None):
		new_table = MappingTable()
		for key in self.__map.keys():
			if keys is not None:
				new_keys = keys.get(key)
			else:
				new_keys = [key]
			if new_keys is not None:
				for new_key in new_keys:
					for value in self.__map[key]:
						if values is not None:
							new_values = mt.get(value)
						else:
							new_values = [value]
						if new_values is not None:
							for new_value in new_values:
								new_table.put(new_key, new_value)
		return new_table

	def inverse(self, include_fallbacks=True):
		new_table = MappingTable()
		for key in self.__map.keys():
			if include_fallbacks:
				for value in self.__map[key]:
					new_table.put(value, key)
			else:
				if len(self.__map[key]) >= 1:
					new_table.put(self.__map[key][0], key)
		return new_table

def load_unicode_mapping_table(filename, source_column=1, target_column=2):
	def col_to_int(v):
		if v.startswith("0x"):
			return int(v, 16)
		else:
			return int(v)
	m_table = MappingTable()
	with open(filename, 'r') as f:
		i = 0
		for line in f:
			line = line.strip()
			if (not line.startswith("#")) and (len(line) >= 1):
				columns = line.split("\t")
				if source_column is None:
					src = i
				else:
					src = col_to_int(columns[source_column - 1])
				dst = col_to_int(columns[target_column - 1])
				m_table.put(src, dst)
				i += 1
	return m_table

def patch_ansi_control_chars(m_table):
	new_table = copy.deepcopy(m_table)
	for i in range(32):
		new_table.remove(i)
	new_table.put(0x01, 0x263A)
	new_table.put(0x02, 0x263B)
	new_table.put(0x03, 0x2665)
	new_table.put(0x04, 0x2666)
	new_table.put(0x05, 0x2663)
	new_table.put(0x06, 0x2660)
	new_table.put(0x07, 0x2022)
	new_table.put(0x08, 0x25D8)
	new_table.put(0x09, 0x25CB)
	new_table.put(0x0A, 0x25D9)
	new_table.put(0x0B, 0x2642)
	new_table.put(0x0C, 0x2640)
	new_table.put(0x0D, 0x266A)
	new_table.put(0x0E, 0x266B)
	new_table.put(0x0F, 0x263C)
	new_table.put(0x10, 0x25BA)
	new_table.put(0x11, 0x25C4)
	new_table.put(0x12, 0x2195)
	new_table.put(0x13, 0x203C)
	new_table.put(0x14, 0x00B6)
	new_table.put(0x15, 0x00A7)
	new_table.put(0x16, 0x25AC)
	new_table.put(0x17, 0x21A8)
	new_table.put(0x18, 0x2191)
	new_table.put(0x19, 0x2193)
	new_table.put(0x1A, 0x2192)
	new_table.put(0x1B, 0x2190)
	new_table.put(0x1C, 0x2319)
	new_table.put(0x1D, 0x2194)
	new_table.put(0x1E, 0x25B2)
	new_table.put(0x1F, 0x25BC)
	new_table.remove(0x7F)
	new_table.put(0x7F, 0x2302)
	return new_table