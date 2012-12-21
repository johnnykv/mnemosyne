# Copyright (C) 2012 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
from normalizers import basenormalizer
from normalizers import glastopf_events


class Mnemosyne(object):
    def __init__(self):
        self.normalizers = {}

        for n in basenormalizer.BaseNormalizer.__subclasses__():
            normalizer = n()
            for channel in normalizer.channels:
                if channel in self.normalizers:
                    raise Exception('Only one normalizer for each channel allowed (%s).' % (channel,))
                else:
                    self.normalizers[channel] = normalizer
        #print self.normalizers

    def normalize(self, data, channel):
        if channel in self.normalizers:
            return self.normalizers[channel].normalizer(channel)
        else:
            raise Exception('No normalizer could be found for %s.' % (channel,))

if __name__ == '__main__':
    m = Mnemosyne()