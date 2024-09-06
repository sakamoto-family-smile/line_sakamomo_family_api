from .edinet_wrapper import EdinetWrapper
from argparse import ArgumentParser


def main(duration_month: int):
    pass


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--duration_month", default=12, help="一覧取得対象の期間（月）を設定する")
    args = parser.parse_args()
    main(duration_month=int(args.duration_month))
