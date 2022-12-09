# I'm aware about heredocuments, but don't like them
#

USERNAME="$1"
USER_HOME=$(eval echo ~"$USERNAME")

WALLPAPERS="$(mktemp -d)"
git clone https://github.com/elementary/wallpapers.git "$WALLPAPERS"


SIJI_FONT_DIR="$(mktemp -d)"
git clone https://github.com/stark/siji "$SIJI_FONT_DIR"
pushd "$SIJI_FONT_DIR"
    ./install.sh -d ${USER_HOME}/.fonts
popd

# misc
echo 'net.ipv6.conf.all.disable_ipv6 = 1' >> /etc/sysctl.conf
mkdir -p ${USER_HOME}/Images
cp -r "${WALLPAPERS}/backgrounds" ${USER_HOME}/Images


# vim plugin manager
curl -fLo ${USER_HOME}/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# scripts
mkdir -p ${USER_HOME}/.scripts
echo '#!/bin/bash'                                      > ${USER_HOME}/.scripts/autochanging_wallpaper.sh
echo 'while true'                                      >> ${USER_HOME}/.scripts/autochanging_wallpaper.sh
echo 'do'                                              >> ${USER_HOME}/.scripts/autochanging_wallpaper.sh
echo "  feh --randomize --bg-fill ${USER_HOME}/Images/backgrounds" >> ${USER_HOME}/.scripts/autochanging_wallpaper.sh
echo '  sleep 1h'                                      >> ${USER_HOME}/.scripts/autochanging_wallpaper.sh
echo 'done'                                            >> ${USER_HOME}/.scripts/autochanging_wallpaper.sh


echo '#!/bin/bash'                                           > ${USER_HOME}/.scripts/make_screenshot.sh
echo ''                                                     >> ${USER_HOME}/.scripts/make_screenshot.sh
echo 'TEMP_DIR=$(mktemp -d)'                                >> ${USER_HOME}/.scripts/make_screenshot.sh
echo 'pushd $TEMP_DIR'                                      >> ${USER_HOME}/.scripts/make_screenshot.sh
echo '    scrot'                                            >> ${USER_HOME}/.scripts/make_screenshot.sh
echo '    xclip -i -selection clipboard -t image/png *.png' >> ${USER_HOME}/.scripts/make_screenshot.sh
echo 'popd'                                                 >> ${USER_HOME}/.scripts/make_screenshot.sh

chmod +x ${USER_HOME}/.scripts/autochanging_wallpaper.sh
chmod +x ${USER_HOME}/.scripts/make_screenshot.sh

# bashrc
echo "bind 'set completion-ignore-case on'"       > ${USER_HOME}/.bashrc
echo 'export EDITOR=vim'                         >> ${USER_HOME}/.bashrc
echo "export PATH=$PATH:${USER_HOME}/.cargo/bin:${USER_HOME}/.scripts" >> ${USER_HOME}/.bashrc

# fishrc
mkdir -p ${USER_HOME}/.config/fish/
echo "set -gx PATH $PATH ${USER_HOME}/.cargo/bin ${USER_HOME}/.scripts ${USER_HOME}/.local/bin" >> ${USER_HOME}/.config/fish/config.fish
echo 'set -gx EDITOR (command -v vim)'                         >> ${USER_HOME}/.config/fish/config.fish

# Xinit
echo 'sxhkd &'                                           > ${USER_HOME}/.xinitrc
echo "xset +fp $(echo ${USER_HOME}/.fonts)"              >> ${USER_HOME}/.xinitrc
echo "xset fp rehash"                                    >> ${USER_HOME}/.xinitrc
echo 'picom &'                                           >> ${USER_HOME}/.xinitrc
echo 'clipmenud &'                                       >> ${USER_HOME}/.xinitrc
echo 'setxkbmap -option grp:alt_shift_toggle dvorak,ru'  >> ${USER_HOME}/.xinitrc
echo "${USER_HOME}/.config/polybar/launch.sh --forest &" >> ${USER_HOME}/.xinitrc
echo "${USER_HOME}/.scripts/autochanging_wallpaper.sh &" >> ${USER_HOME}/.xinitrc
echo 'exec bspwm'                                        >> ${USER_HOME}/.xinitrc

# picom

echo "shadow = true;"                                                             >> ${USER_HOME}/.config/picom.conf
echo "no-dnd-shadow = true;"                                                      >> ${USER_HOME}/.config/picom.conf
echo "no-dock-shadow = true;"                                                     >> ${USER_HOME}/.config/picom.conf
echo "clear-shadow = true;"                                                       >> ${USER_HOME}/.config/picom.conf
echo "shadow-radius = 7;"                                                         >> ${USER_HOME}/.config/picom.conf
echo "shadow-offset-x = -7;"                                                      >> ${USER_HOME}/.config/picom.conf
echo "shadow-offset-y = -7;"                                                      >> ${USER_HOME}/.config/picom.conf
echo "shadow-exclude = ["                                                         >> ${USER_HOME}/.config/picom.conf
echo "	\"name = 'Notification'\","                                               >> ${USER_HOME}/.config/picom.conf
echo "	\"class_g = 'Conky'\","                                                   >> ${USER_HOME}/.config/picom.conf
echo "	\"class_g ?= 'Notify-osd'\","                                             >> ${USER_HOME}/.config/picom.conf
echo "	\"class_g = 'Cairo-clock'\","                                             >> ${USER_HOME}/.config/picom.conf
echo "	\"_GTK_FRAME_EXTENTS@:c\""                                                >> ${USER_HOME}/.config/picom.conf
echo "];"                                                                         >> ${USER_HOME}/.config/picom.conf
echo ""                                                                           >> ${USER_HOME}/.config/picom.conf
echo "menu-opacity = 0.8;"                                                        >> ${USER_HOME}/.config/picom.conf
echo "inactive-opacity = 0.9;"                                                    >> ${USER_HOME}/.config/picom.conf
echo "frame-opacity = 0.7;"                                                       >> ${USER_HOME}/.config/picom.conf
echo "inactive-opacity-override = true;"                                          >> ${USER_HOME}/.config/picom.conf
echo "alpha-step = 0.06;"                                                         >> ${USER_HOME}/.config/picom.conf
echo "blur-kern = \"3x3box\";"                                                    >> ${USER_HOME}/.config/picom.conf
echo "blur-background-exclude = ["                                                >> ${USER_HOME}/.config/picom.conf
echo "	\"window_type = 'dock'\","                                                >> ${USER_HOME}/.config/picom.conf
echo "	\"window_type = 'desktop'\","                                             >> ${USER_HOME}/.config/picom.conf
echo "	\"_GTK_FRAME_EXTENTS@:\""                                                 >> ${USER_HOME}/.config/picom.conf
echo "];"                                                                         >> ${USER_HOME}/.config/picom.conf
echo ""                                                                           >> ${USER_HOME}/.config/picom.conf
echo "glx-copy-from-front = false;"                                               >> ${USER_HOME}/.config/picom.conf
echo "glx-swap-method = \"undefined\";"                                           >> ${USER_HOME}/.config/picom.conf
echo ""                                                                           >> ${USER_HOME}/.config/picom.conf
echo "wintypes:"                                                                  >> ${USER_HOME}/.config/picom.conf
echo "{"                                                                          >> ${USER_HOME}/.config/picom.conf
echo "  tooltip = { fade = true; shadow = true; opacity = 0.75; focus = true; };" >> ${USER_HOME}/.config/picom.conf
echo "};"                                                                         >> ${USER_HOME}/.config/picom.conf


# synaptics

mkdir -p /etc/X11/xorg.conf.d/
echo 'Section "InputClass"'                           > /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Identifier "touchpad catchall"'        >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Driver "synaptics"'                    >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        MatchIsTouchpad "on"'                  >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "VertEdgeScroll" "on"'          >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo                                                 >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "CircularScrolling"     "on"'   >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "CircScrollTrigger"     "3"'    >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "CircScrollDelta"       "0.01"' >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo                                                 >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "PalmDetect"            "0.01"' >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo                                                 >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "VertTwoFingerScroll"   "on"'   >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "VertScrollDelta"       "30"'   >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "HorizScrollDelta"      "30"'   >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "TapButton1"            "1"'    >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "TapButton2"            "3"'    >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo '        Option "TapButton3"            "2"'    >> /etc/X11/xorg.conf.d/50-synaptics.conf
echo 'EndSection'                                    >> /etc/X11/xorg.conf.d/50-synaptics.conf

# Vim
echo 'set number'         >> ${USER_HOME}/.vimrc
echo 'set relativenumber' >> ${USER_HOME}/.vimrc
echo                      >> ${USER_HOME}/.vimrc
echo 'set hlsearch'       >> ${USER_HOME}/.vimrc
echo 'set incsearch'      >> ${USER_HOME}/.vimrc
echo                      >> ${USER_HOME}/.vimrc
echo 'set wildmenu'       >> ${USER_HOME}/.vimrc
echo 'set nocompatible'   >> ${USER_HOME}/.vimrc
echo                      >> ${USER_HOME}/.vimrc
echo 'set tabstop=8'      >> ${USER_HOME}/.vimrc
echo 'set softtabstop=0'  >> ${USER_HOME}/.vimrc
echo 'set expandtab'      >> ${USER_HOME}/.vimrc
echo 'set shiftwidth=4'   >> ${USER_HOME}/.vimrc
echo 'set smarttab'       >> ${USER_HOME}/.vimrc
echo                      >> ${USER_HOME}/.vimrc
echo 'syntax on'          >> ${USER_HOME}/.vimrc
echo                      >> ${USER_HOME}/.vimrc

echo 'nnoremap <C-j> :m .+1<CR>'          >> ${USER_HOME}/.vimrc
echo 'nnoremap <C-k> :m .-2<CR>'          >> ${USER_HOME}/.vimrc
echo                                      >> ${USER_HOME}/.vimrc
echo 'inoremap <C-j> <ESC>:m .+1<CR>==gi' >> ${USER_HOME}/.vimrc
echo 'inoremap <C-k> <ESC>:m .-2<CR>==gi' >> ${USER_HOME}/.vimrc
echo                                      >> ${USER_HOME}/.vimrc
echo "vnoremap <C-j> :m '>1<CR>gv=gv"     >> ${USER_HOME}/.vimrc
echo "vnoremap <C-k> :m '<2<CR>gv=gv"     >> ${USER_HOME}/.vimrc
echo                                      >> ${USER_HOME}/.vimrc
echo "let mapleader = ' '"                >> ${USER_HOME}/.vimrc

echo "call plug#begin('${USER_HOME}/.vim/plugged')"      >> ${USER_HOME}/.vimrc
echo                                          >> ${USER_HOME}/.vimrc
echo "Plug 'easymotion/vim-easymotion'"       >> ${USER_HOME}/.vimrc
echo "Plug 'godlygeek/tabular'"               >> ${USER_HOME}/.vimrc
echo "Plug 'luochen1990/rainbow'"             >> ${USER_HOME}/.vimrc
echo "Plug 'mbbill/undotree'"                 >> ${USER_HOME}/.vimrc
echo "Plug 'mkitt/tabline.vim'"               >> ${USER_HOME}/.vimrc
echo "Plug 'nathanaelkane/vim-indent-guides'" >> ${USER_HOME}/.vimrc
echo "Plug 'scrooloose/nerdtree'"             >> ${USER_HOME}/.vimrc
echo "Plug 'sheerun/vim-polyglot'"            >> ${USER_HOME}/.vimrc
echo "Plug 'tpope/vim-fugitive'"              >> ${USER_HOME}/.vimrc
echo "Plug 'tpope/vim-surround'"              >> ${USER_HOME}/.vimrc
echo "Plug 'chrisbra/csv.vim'"                >> ${USER_HOME}/.vimrc
echo "Plug 'lyokha/vim-xkbswitch'"            >> ${USER_HOME}/.vimrc
echo "Plug 'kovetskiy/sxhkd-vim'"             >> ${USER_HOME}/.vimrc
echo "Plug 'tpope/vim-repeat'"                >> ${USER_HOME}/.vimrc
echo "Plug 'junegunn/fzf.vim'"                >> ${USER_HOME}/.vimrc
echo "Plug 'blueyed/vim-diminactive'"         >> ${USER_HOME}/.vimrc
echo "Plug 'unblevable/quick-scope'"          >> ${USER_HOME}/.vimrc
echo "Plug 'wlangstroth/vim-racket'"          >> ${USER_HOME}/.vimrc
echo "Plug 'calebsmith/vim-lambdify'"         >> ${USER_HOME}/.vimrc
echo "Plug 'ntpeters/vim-better-whitespace'"  >> ${USER_HOME}/.vimrc
echo "Plug 'mhinz/vim-signify'"               >> ${USER_HOME}/.vimrc
echo "Plug 'wsdjeg/vim-fetch'"                >> ${USER_HOME}/.vimrc
echo "Plug 'Galicarnax/vim-regex-syntax'"     >> ${USER_HOME}/.vimrc
echo "Plug 'baverman/vial'"                   >> ${USER_HOME}/.vimrc
echo "Plug 'baverman/vial-http'"              >> ${USER_HOME}/.vimrc
echo                                          >> ${USER_HOME}/.vimrc
echo "Plug 'prabirshrestha/vim-lsp'"          >> ${USER_HOME}/.vimrc
echo "Plug 'mattn/vim-lsp-settings'"          >> ${USER_HOME}/.vimrc
echo "Plug 'Shougo/ddc.vim'"                  >> ${USER_HOME}/.vimrc
echo "Plug 'shun/ddc-vim-lsp'"                >> ${USER_HOME}/.vimrc
echo                                          >> ${USER_HOME}/.vimrc
echo "call plug#end()"                        >> ${USER_HOME}/.vimrc
echo                                          >> ${USER_HOME}/.vimrc
echo 'map <C-n> :NERDTreeToggle<CR>'                 >> ${USER_HOME}/.vimrc
echo 'map U :UndotreeToggle<CR>'                     >> ${USER_HOME}/.vimrc
echo 'map <leader>n :Files<CR>'                      >> ${USER_HOME}/.vimrc
echo 'map <C-/> :Rg<CR>'                             >> ${USER_HOME}/.vimrc
echo 'map gG :G<CR>'                                 >> ${USER_HOME}/.vimrc
echo 'map <C-s> :VialHttp<CR>'                       >> ${USER_HOME}/.vimrc
echo                                                 >> ${USER_HOME}/.vimrc
echo 'set updatetime=100'                            >> ${USER_HOME}/.vimrc
echo                                                 >> ${USER_HOME}/.vimrc
echo 'let g:rainbow_active = 1'                      >> ${USER_HOME}/.vimrc
echo 'let g:indent_guides_enable_on_vim_startup = 1' >> ${USER_HOME}/.vimrc
echo 'let g:XkbSwitchEnabled = 1'                    >> ${USER_HOME}/.vimrc
echo 'let g:diminactive_use_syntax = 1'              >> ${USER_HOME}/.vimrc
echo "let g:qs_highlight_on_keys = ['f', 'F', 't', 'T']" >> ${USER_HOME}/.vimrc
echo                                                 >> ${USER_HOME}/.vimrc
echo 'autocmd VimEnter * DimInactiveOn'              >> ${USER_HOME}/.vimrc
echo                                                 >> ${USER_HOME}/.vimrc
echo 'let g:diminactive_use_syntax = 1'              >> ${USER_HOME}/.vimrc
echo 'let g:diminactive_use_colorcolumn = 0'         >> ${USER_HOME}/.vimrc
echo                                                 >> ${USER_HOME}/.vimrc
echo "function! s:on_lsp_buffer_enabled() abort"                                >> ${USER_HOME}/.vimrc
echo "    setlocal omnifunc=lsp#complete"                                       >> ${USER_HOME}/.vimrc
echo "    setlocal signcolumn=yes"                                              >> ${USER_HOME}/.vimrc
echo "    if exists('+tagfunc') | setlocal tagfunc=lsp#tagfunc | endif"         >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> gd <plug>(lsp-definition)"                              >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> g/ <plug>(lsp-document-symbol-search)"                  >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> g? <plug>(lsp-workspace-symbol-search)"                 >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> gr <plug>(lsp-references)"                              >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> gi <plug>(lsp-implementation)"                          >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> <leader>r <plug>(lsp-rename)"                           >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> <leader>i <plug>(lsp-next-diagnostic)"                  >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> <leader>I <plug>(lsp-previous-diagnostic)"              >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> K <plug>(lsp-hover) <bar> :syntax on"                   >> ${USER_HOME}/.vimrc
echo "    nmap <buffer> <leader>d <plug>(lsp-document-diagnostics)"             >> ${USER_HOME}/.vimrc
echo                                                                            >> ${USER_HOME}/.vimrc
echo "    let g:lsp_format_sync_timeout = 1000"                                 >> ${USER_HOME}/.vimrc
echo "    autocmd! BufWritePre *.rs,*.go call execute('LspDocumentFormatSync')" >> ${USER_HOME}/.vimrc
echo "endfunction"                                                              >> ${USER_HOME}/.vimrc

echo "augroup lsp_install"                                                >> ${USER_HOME}/.vimrc
echo "    au!"                                                            >> ${USER_HOME}/.vimrc
echo "    autocmd User lsp_buffer_enabled call s:on_lsp_buffer_enabled()" >> ${USER_HOME}/.vimrc
echo "augroup END"                                                        >> ${USER_HOME}/.vimrc


git clone https://github.com/grwlf/xkb-switch.git;
pushd xkb-switch;
    mkdir build;
    pushd build;
        cmake ..;
        make -j$(nproc);
        make -j$(nproc) install;
        ldconfig;
    popd;
popd
rm -rf xkb-switch


# tmux
git clone https://github.com/tmux-plugins/tpm /etc/tmux/plugins/tpm
echo 'set -g prefix C-a'                                       > ${USER_HOME}/.tmux.conf
echo ''                                                       >> ${USER_HOME}/.tmux.conf
echo 'set-option -g default-shell /bin/fish'                  >> ${USER_HOME}/.tmux.conf
echo ''                                                       >> ${USER_HOME}/.tmux.conf
echo 'bind C-a send-prefix'                                   >> ${USER_HOME}/.tmux.conf
echo 'unbind C-b'                                             >> ${USER_HOME}/.tmux.conf
echo 'set -sg escape-time 1'                                  >> ${USER_HOME}/.tmux.conf
echo 'set -g base-index 1'                                    >> ${USER_HOME}/.tmux.conf
echo 'setw -g pane-base-index 1'                              >> ${USER_HOME}/.tmux.conf
echo 'setw -g repeat-time 1000'                               >> ${USER_HOME}/.tmux.conf
echo "bind r source-file ${USER_HOME}/.tmux.conf \; display 'Reloaded!'" >> ${USER_HOME}/.tmux.conf
echo                                                          >> ${USER_HOME}/.tmux.conf
echo 'bind | split-window -h -c "#{pane_current_path}"'       >> ${USER_HOME}/.tmux.conf
echo 'bind - split-window -v -c "#{pane_current_path}"'       >> ${USER_HOME}/.tmux.conf
echo 'bind c new-window -c      "#{pane_current_path}"'       >> ${USER_HOME}/.tmux.conf
echo                                                          >> ${USER_HOME}/.tmux.conf
echo 'bind h select-pane -L'                                  >> ${USER_HOME}/.tmux.conf
echo 'bind j select-pane -D'                                  >> ${USER_HOME}/.tmux.conf
echo 'bind k select-pane -U'                                  >> ${USER_HOME}/.tmux.conf
echo 'bind l select-pane -R'                                  >> ${USER_HOME}/.tmux.conf
echo                                                          >> ${USER_HOME}/.tmux.conf
echo 'bind -r C-h select-window -t :-'                        >> ${USER_HOME}/.tmux.conf
echo 'bind -r C-l select-window -t :+'                        >> ${USER_HOME}/.tmux.conf
echo                                                          >> ${USER_HOME}/.tmux.conf
echo 'bind -r H resize-pane -L 5'                             >> ${USER_HOME}/.tmux.conf
echo 'bind -r J resize-pane -D 5'                             >> ${USER_HOME}/.tmux.conf
echo 'bind -r K resize-pane -U 5'                             >> ${USER_HOME}/.tmux.conf
echo 'bind -r L resize-pane -R 5'                             >> ${USER_HOME}/.tmux.conf
echo                                                          >> ${USER_HOME}/.tmux.conf
echo 'set -g default-terminal "screen-256color"'              >> ${USER_HOME}/.tmux.conf
echo 'set-window-option -g mode-keys vi'                      >> ${USER_HOME}/.tmux.conf
echo                                                          >> ${USER_HOME}/.tmux.conf
echo 'set -g @plugin "tmux-plugins/tpm"'                      >> ${USER_HOME}/.tmux.conf
echo 'set -g @plugin "tmux-plugins/tmux-resurrect"'           >> ${USER_HOME}/.tmux.conf
echo 'set -g @plugin "tmux-plugins/tmux-cpu"'                 >> ${USER_HOME}/.tmux.conf
echo 'set -g @plugin "jaclu/tmux-power-zoom"'                 >> ${USER_HOME}/.tmux.conf
echo 'set -g @plugin "tmux-plugins/tmux-sidebar"'             >> ${USER_HOME}/.tmux.conf
echo 'set -g @sidebar-tree-command "tree -C"'                 >> ${USER_HOME}/.tmux.conf
echo                                                          >> ${USER_HOME}/.tmux.conf
echo 'set -g @plugin "tmux-plugins/tmux-prefix-highlight"'    >> ${USER_HOME}/.tmux.conf

TMUX_CPU="#{cpu_bg_color} CPU: #{cpu_icon} #{cpu_percentage}"
TMUX_BAT="#{battery_status_bg} Batt: #{battery_icon} #{battery_percentage} #{battery_remain}"
TMUX_PREFIX="#{prefix_highlight}"

echo "set -g status-right \"$TMUX_PREFIX | $TMUX_CPU | $TMUX_BAT | %a %h-%d %H:%M\"" >> ${USER_HOME}/.tmux.conf
echo 'set -g status-right-length "150"'                       >> ${USER_HOME}/.tmux.conf
echo                                                          >> ${USER_HOME}/.tmux.conf
echo 'run "/etc/tmux/plugins/tpm/tpm"'                        >> ${USER_HOME}/.tmux.conf


#warpd
mkdir -p ${USER_HOME}/.config/warpd
echo 'activation_key: M-/'             >> ${USER_HOME}/.config/warpd/config
echo 'hint: C'                         >> ${USER_HOME}/.config/warpd/config
echo 'hint2: c'                        >> ${USER_HOME}/.config/warpd/config
echo 'exit: esc'                       >> ${USER_HOME}/.config/warpd/config
echo 'drag: v'                         >> ${USER_HOME}/.config/warpd/config
echo 'copy_and_exit: y'                >> ${USER_HOME}/.config/warpd/config
echo 'accelerator: space'              >> ${USER_HOME}/.config/warpd/config
echo 'buttons: Alt_L underscore Alt_R' >> ${USER_HOME}/.config/warpd/config
echo 'history: colon'                  >> ${USER_HOME}/.config/warpd/config
echo 'grid: g'                         >> ${USER_HOME}/.config/warpd/config
echo 'screen: s'                       >> ${USER_HOME}/.config/warpd/config
echo 'left: h'                         >> ${USER_HOME}/.config/warpd/config
echo 'down: j'                         >> ${USER_HOME}/.config/warpd/config
echo 'up: k'                           >> ${USER_HOME}/.config/warpd/config
echo 'right: l'                        >> ${USER_HOME}/.config/warpd/config
echo 'top: H'                          >> ${USER_HOME}/.config/warpd/config
echo 'middle: M'                       >> ${USER_HOME}/.config/warpd/config
echo 'bottom: L'                       >> ${USER_HOME}/.config/warpd/config
echo 'start: 0'                        >> ${USER_HOME}/.config/warpd/config
echo 'end: $'                          >> ${USER_HOME}/.config/warpd/config
echo 'scroll_down: C-d'                >> ${USER_HOME}/.config/warpd/config
echo 'scroll_up: C-u'                  >> ${USER_HOME}/.config/warpd/config
echo 'cursor_color: FF4500'            >> ${USER_HOME}/.config/warpd/config
echo 'cursor_size: 7'                  >> ${USER_HOME}/.config/warpd/config
echo 'repeat_interval: 20'             >> ${USER_HOME}/.config/warpd/config
echo 'speed: 220'                      >> ${USER_HOME}/.config/warpd/config
echo 'max_speed: 1600'                 >> ${USER_HOME}/.config/warpd/config
echo 'acceleration: 700'               >> ${USER_HOME}/.config/warpd/config
echo                                   >> ${USER_HOME}/.config/warpd/config
echo 'hint_bgcolor: 00ff00'            >> ${USER_HOME}/.config/warpd/config
echo 'hint_fgcolor: 000000'            >> ${USER_HOME}/.config/warpd/config
echo 'hint_undo: u'                    >> ${USER_HOME}/.config/warpd/config
echo 'scroll_speed: 300'               >> ${USER_HOME}/.config/warpd/config
echo 'scroll_max_speed: 9000'          >> ${USER_HOME}/.config/warpd/config
echo 'scroll_acceleration: 2600'       >> ${USER_HOME}/.config/warpd/config
echo 'indicator: topleft'              >> ${USER_HOME}/.config/warpd/config
echo 'indicator_color: 00ff00'         >> ${USER_HOME}/.config/warpd/config
echo 'indicator_size: 22'              >> ${USER_HOME}/.config/warpd/config


# bspwm
mkdir -p ${USER_HOME}/.config/bspwm
touch ${USER_HOME}/.config/bspwm/bspwmrc
chmod +x ${USER_HOME}/.config/bspwm/bspwmrc
echo '#!/bin/sh'                                      > ${USER_HOME}/.config/bspwm/bspwmrc
echo 'bspc monitor -d I II III IV V VI VII VIII IX X' >> ${USER_HOME}/.config/bspwm/bspwmrc
echo 'bspc config border_width 2'                     >> ${USER_HOME}/.config/bspwm/bspwmrc
echo 'bspc config borderless_monocle true'            >> ${USER_HOME}/.config/bspwm/bspwmrc
echo 'bspc config gapless_monocle true'               >> ${USER_HOME}/.config/bspwm/bspwmrc
echo 'bspc config focus_follows_pointer true'         >> ${USER_HOME}/.config/bspwm/bspwmrc

# sxhkd
mkdir -p ${USER_HOME}/.config/sxhkd
touch ${USER_HOME}/.config/sxhkd/sxhkdrc

echo '#!/bin/sh'                               > ${USER_HOME}/.config/sxhkd/sxhkdrc

echo 'super + shift + {z,a}'                  >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' bspc node @/ -C {forward,backward}'    >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + Return'                         >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' st -e tmux'                            >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo                                          >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + c'                              >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' CM_LAUNCHER=rofi clipmenu -i'          >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo                                          >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + Tab'                            >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' setxkbmap -option grp:alt_shift_toggle {dvorak, us},ru' >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo                                          >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'Print'                                  >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' flameshot gui'                         >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo                                          >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + t'                                      >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo " bash ${USER_HOME}/.config/polybar/scripts/colors_rofi.sh" >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo                                                  >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'XF86AudioRaiseVolume'      >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' amixer set Master 2%+'    >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'XF86AudioLowerVolume'      >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' amixer set Master 2%-'    >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'XF86AudioMute'             >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' amixer set Master toggle' >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'XF86MonBrightnessUp'       >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' xbacklight +5'            >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'XF86MonBrightnessDown'     >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' xbacklight -5'            >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo                                          >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + n'                              >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' firefox'                               >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + f'                              >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' bspc node -t ~fullscreen'              >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + shift + Return'                 >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' pkill -USR1 -x sxhkd'                  >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + {j,k,l,p}'                      >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' bspc node -f {west,south,north,east}'  >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + d'                              >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' rofi -show run'                        >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + shift + d'                      >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' rofi -show drun'                       >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + shift + q'                      >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' bspc node -{c,k}'                      >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + {_,shift + }{1-9,0}'            >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo " bspc {desktop -f,node -d} '^{1-9,10}'" >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + r'                              >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' bspc node @/ -R 90'                    >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo 'super + space'                          >> ${USER_HOME}/.config/sxhkd/sxhkdrc
echo ' bspc node -t {floating, tiled}'        >> ${USER_HOME}/.config/sxhkd/sxhkdrc


echo "permit ${USERNAME} as root"  > /etc/doas.conf
echo "permit root as ${USERNAME}" >> /etc/doas.conf
echo "permit nopass root" >> /etc/doas.conf


git config --global core.editor vim
cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime


chown -R ${USERNAME} ${USER_HOME}

doas -u ${USERNAME} vim +PlugInstall +qa
VIM_LSP_SETTINGS_SERVERS="${USER_HOME}/.local/share/vim-lsp-settings/servers"
VIM_LSP_SETTINGS_ROOT="${USER_HOME}/.vim/plugged/vim-lsp-settings/installer"
mkdir -p ${VIM_LSP_SETTINGS_SERVERS}

cd ${VIM_LSP_SETTINGS_SERVERS}
    for s in cmake-language-server \
             bash-language-server \
             clangd \
             docker-langserver \
             html-languageserver \
             json-languageserver \
             omnisharp-lsp \
             powershell-languageserver \
             pylsp-all \
             sql-language-server \
             vim-language-server \
             rust-analyzer
    do
        mkdir $s
        cd $s
            sh ${VIM_LSP_SETTINGS_ROOT}/install-$s.sh
        cd -
    done

doas -u ${USERNAME} fish -c 'curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher'
doas -u ${USERNAME} fish -c 'fisher install jethrokuan/z'
doas -u ${USERNAME} fish -c 'fisher install IlanCosman/tide@v5'


# polybar
#
doas -u ${USERNAME} bash -c "
mkdir -p ${USER_HOME}/.config/polybar;
touch ${USER_HOME}/.config/polybar/config;
git clone https://github.com/adi1090x/polybar-themes;
cd polybar-themes/;
    echo 1 | ./setup.sh;
    fc-cache -v;
cd -;
rm -rf polybar-themes;
"

#sed -i '/font-1.*=.*"/ s/"[^"]*"/"Wuncon Siji:size=11"/' ${USER_HOME}/.config/polybar/config.ini
