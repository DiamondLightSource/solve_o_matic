import os
import sys

if not 'CCP4' in os.environ:
    raise RuntimeError('CCP4 not defined')

symop_lib = os.path.join(os.environ['CCP4'], 'lib', 'data', 'symop.lib')

if not os.path.exists(symop_lib):
    raise RuntimeError('CCP4 symmetry library missing: %s' % symop_lib)

class symmetry_information:

    def __init__(self):

        self._number_to_short_name = { }
        self._short_name_to_number = { }
        self._short_name_to_long_name = { }
        self._long_name_to_short_name = { }
        self._short_name_to_pointgroup = { }

        for record in open(symop_lib):
            if not record.strip():
                continue

            if ' ' in record[:1]:
                continue

            tokens = record.split()
            number = int(tokens[0])
            short_name = tokens[3]
            pointgroup = tokens[4]
            long_name = record.split('\'')[1]

            self._number_to_short_name[number] = short_name
            self._short_name_to_number[short_name] = number
            self._short_name_to_long_name[short_name] = long_name
            self._long_name_to_short_name[long_name] = short_name
            self._short_name_to_pointgroup[short_name] = pointgroup

            # cope with long names with no spaces, e.g. P1211

            long_name_ns = long_name.replace(' ', '')
            if not long_name_ns in self._long_name_to_short_name:
                self._long_name_to_short_name[long_name_ns] = short_name

        return

    def get_long_name(self, short_name):
        if not short_name in self._short_name_to_long_name:
            raise RuntimeError('short name %s not known' % short_name)

        return self._short_name_to_long_name[short_name]

    def get_short_name(self, long_name):

        if long_name in self._short_name_to_long:
            return long_name

        if not long_name in self._long_name_to_short_name:
            raise RuntimeError('long name %s not known' % long_name)

        return self._long_name_to_short_name[long_name]

    def get_number(self, short_name):

        if short_name in self._long_name_to_short_name:
            short_name = self._long_name_to_short_name[short_name]

        if not short_name in self._short_name_to_number:
            raise RuntimeError('short name %s not known' % short_name)

        return self._short_name_to_number[short_name]

    def get_pointgroup(self, short_name):

        if ':' in short_name:
            if short_name == 'R32:H':
                short_name = 'H32'
            if short_name == 'R3:H':
                short_name = 'H3'

        if short_name in self._long_name_to_short_name:
            short_name = self._long_name_to_short_name[short_name]

        if not short_name in self._short_name_to_pointgroup:
            raise RuntimeError('short name %s not known' % short_name)

        return self._short_name_to_pointgroup[short_name]

if __name__ == '__main__':
    si = symmetry_information()

    print(si.get_pointgroup('P212121'))
    print(si.get_pointgroup('P 21 21 21'))
