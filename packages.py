from entity import Package


PACKAGE_LIST = [
    Package('media-libs/libpng', use_flags='apng'),
    Package('@world', '-uDNv --with-bdeps=y --backtrack=100'),
    Package('media-libs/libpng', use_flags='apng'),
    Package('sys-libs/ncurses', use_flags='-gpm'),
    Package('app-editors/vim', use_flags='python vim-pager perl terminal')
]
