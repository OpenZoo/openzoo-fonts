from .tables import MappingTable

def generate_jis0208_to_little_limit_mapping_table():
	m_table = MappingTable()
	for iy in range(0, 94):
		for ix in range(0, 94):
			m_table.put(((iy + 0x21) * 256) + (ix + 0x21), iy * 94 + ix)
	return m_table
