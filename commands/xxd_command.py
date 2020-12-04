from .command import Command
from parsers import Parsers


class XxdCommand(Command):
    def __init__(self, cli):
        super().__init__(cli)
        self.parser = Parsers.xxd_parser(file=self.cli.out)

    def execute(self, params=''):
        try:
            params = self.split_with_quotes(params)
            args = self.parser.parse_args(params)
        except ValueError:
            return

        try:
            buf = b''
            total_blocks = 0
            for data in self.cli.file_system.get_file_data_by_path(args.path):
                buf += data
                cur_bytes = buf[:(len(buf) // 16) * 16]
                buf = buf[len(cur_bytes):]
                for i in range(len(cur_bytes) // 16):
                    block = cur_bytes[i * 16:(i + 1) * 16]
                    self.cli.print(self.format_block(total_blocks, block))
                    total_blocks += 1
            if buf:
                self.cli.print(self.format_block(total_blocks, buf))
        except FileNotFoundError:
            self.cli.print_error("There isn't such file on image", end=' ')
            self.cli.print(args.path)

    @staticmethod
    def format_block(block_num, data):
        ans = hex(block_num * 16)[2:].rjust(8, '0') + ': '
        double_bytes = []
        for j in range((len(data) + 1) // 2):
            pair = ''.join(hex(b)[2:].rjust(2, '0')
                           for b in data[2 * j:2 * (j + 1)])
            double_bytes.append(pair)
        ans += ' '.join(double_bytes)

        asci_presentation = ''.join(chr(b) if 0x20 <= b <= 0x7d else '.'
                                    for b in data)
        ans = ans.ljust(49, ' ')
        ans += '  '
        ans += asci_presentation
        return ans
