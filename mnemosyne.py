    # def __init__(self):
    #     self.normalizers = {}

    #     for n in basenormalizer.BaseNormalizer.__subclasses__():
    #         normalizer = n()
    #         for channel in normalizer.channels:
    #             if channel in self.normalizers:
    #                 self.normalizers[channel].append(n)
    #             else:
    #                 self.normalizers[channel] = [n, ]
    #     print self.normalizers

    # def normalize(self, data, channel):
    #     if channel in self.normalizers:
    #         return self.normalizers[channel].normalize(data)
    #     else:
    #         raise Exception('No normalizer could be found for %s.' % (channel,))