

" Set file type detection and syntax highlighting
filetype plugin on
syntax on

" Set tab settings
set expandtab
set tabstop=4
set shiftwidth=4

" Show line numbers
set number

" Show the current line and column numbers
set ruler

" Set up autoindentation for Python code
autocmd FileType python setlocal autoindent

" Set up PEP8 indentation rules for Python code
autocmd FileType python setlocal shiftwidth=4 softtabstop=4 expandtab
