syntax on

" Filetype detection
augroup filetype_detection
    autocmd!
    autocmd BufNewFile,BufReadPost *.yml,*.yaml setfiletype yaml
    autocmd BufNewFile,BufReadPost *.py setfiletype python
    autocmd BufNewFile,BufReadPost *.ini setfiletype ini
    autocmd BufNewFile,BufReadPost *.json setfiletype json
augroup END

" YAML-specific settings
augroup yaml_settings
    autocmd!
    autocmd FileType yaml setlocal ai ts=2 sw=2 et nu cuc
augroup END

" Python-specific settings
augroup python_settings
    autocmd!
    autocmd FileType python setlocal ai ts=4 sw=4 et
augroup END

" INI-specific settings
augroup ini_settings
    autocmd!
    autocmd FileType ini setlocal ai ts=2 sw=2 et
augroup END

" JSON-specific settings
augroup json_settings
    autocmd!
    autocmd FileType json setlocal ai ts=4 sw=4 et
augroup END
