#!/usr/bin/env bash

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
cat << EOF > ${USER_HOME}/.scripts/autochanging_wallpaper.sh
#!/bin/bash
while true
do
  feh --randomize --bg-fill ${USER_HOME}/Images/backgrounds
  sleep 1h
done
EOF


cat << "EOF" > ${USER_HOME}/.scripts/make_screenshot.sh
#!/bin/bash

TEMP_DIR=$(mktemp -d)
pushd $TEMP_DIR
    scrot
    xclip -i -selection clipboard -t image/png *.png
popd
EOF

chmod +x ${USER_HOME}/.scripts/autochanging_wallpaper.sh
chmod +x ${USER_HOME}/.scripts/make_screenshot.sh

cat << "EOF" > ${USER_HOME}/.bashrc
bind 'set completion-ignore-case on'
export EDITOR=vim
export PATH=$PATH:${USER_HOME}/.cargo/bin:${USER_HOME}/.scripts
EOF

# fishrc
mkdir -p ${USER_HOME}/.config/fish/
cat << EOF >> ${USER_HOME}/.config/fish/config.fish
set -gx PATH \$PATH ${USER_HOME}/.cargo/bin ${USER_HOME}/.scripts ${USER_HOME}/.local/bin
set -gx EDITOR (command -v vim)
EOF

# Xinit
cat << EOF > ${USER_HOME}/.xinitrc
sxhkd &
xset +fp \$(echo ${USER_HOME}/.fonts)
xset fp rehash
picom &
clipmenud &
setxkbmap -option grp:alt_shift_toggle dvorak,ru
${USER_HOME}/.config/polybar/launch.sh --forest &
${USER_HOME}/.scripts/autochanging_wallpaper.sh &
exec bspwm
EOF

# picom

cat << EOF > ${USER_HOME}/.config/picom.conf
shadow = true;
no-dnd-shadow = true;
no-dock-shadow = true;
clear-shadow = true;
shadow-radius = 7;
shadow-offset-x = -7;
shadow-offset-y = -7;
shadow-exclude = [
	"name = 'Notification'",
	"class_g = 'Conky'",
	"class_g ?= 'Notify-osd'",
	"class_g = 'Cairo-clock'",
];

inactive-opacity = 0.9;
frame-opacity = 0.7;
inactive-opacity-override = true;
alpha-step = 0.06;
blur-kern = "3x3box";
blur-background-exclude = [
	"window_type = 'dock'",
	"window_type = 'desktop'",
];

glx-copy-from-front = false;

wintypes:
{
  tooltip = { fade = true; shadow = true; opacity = 0.75; focus = true; };
};
EOF


# synaptics

mkdir -p /etc/X11/xorg.conf.d/
cat << EOF > /etc/X11/xorg.conf.d/50-synaptics.conf
Section "InputClass"
        Identifier "touchpad catchall"
        Driver "synaptics"
        MatchIsTouchpad "on"
        Option "VertEdgeScroll" "on"

        Option "CircularScrolling"     "on"
        Option "CircScrollTrigger"     "3"
        Option "CircScrollDelta"       "0.01"

        Option "PalmDetect"            "0.01"

        Option "VertTwoFingerScroll"   "on"
        Option "VertScrollDelta"       "30"
        Option "HorizScrollDelta"      "30"
        Option "TapButton1"            "1"
        Option "TapButton2"            "3"
        Option "TapButton3"            "2"
EndSection
EOF

# Vim
cat << EOF > ${USER_HOME}/.vimrc
set number
set relativenumber

set hlsearch
set incsearch

set wildmenu
set nocompatible

set tabstop=8
set softtabstop=0
set expandtab
set shiftwidth=4
set smarttab

syntax on


nnoremap <C-j> :m .+1<CR>
nnoremap <C-k> :m .-2<CR>

inoremap <C-j> <ESC>:m .+1<CR>==gi
inoremap <C-k> <ESC>:m .-2<CR>==gi

vnoremap <C-j> :m '>1<CR>gv=gv
vnoremap <C-k> :m '<2<CR>gv=gv

let mapleader = ' '

call plug#begin('${USER_HOME}/.vim/plugged')

Plug 'easymotion/vim-easymotion'
Plug 'godlygeek/tabular'
Plug 'luochen1990/rainbow'
Plug 'mbbill/undotree'
Plug 'mkitt/tabline.vim'
Plug 'nathanaelkane/vim-indent-guides'
Plug 'scrooloose/nerdtree'
Plug 'sheerun/vim-polyglot'
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-surround'
Plug 'chrisbra/csv.vim'
Plug 'lyokha/vim-xkbswitch'
Plug 'kovetskiy/sxhkd-vim'
Plug 'tpope/vim-repeat'
Plug 'junegunn/fzf.vim'
Plug 'blueyed/vim-diminactive'
Plug 'unblevable/quick-scope'
Plug 'wlangstroth/vim-racket'
Plug 'calebsmith/vim-lambdify'
Plug 'ntpeters/vim-better-whitespace'
Plug 'mhinz/vim-signify'
Plug 'wsdjeg/vim-fetch'
Plug 'Galicarnax/vim-regex-syntax'
Plug 'baverman/vial'
Plug 'baverman/vial-http'

Plug 'prabirshrestha/vim-lsp'
Plug 'mattn/vim-lsp-settings'
Plug 'SirVer/ultisnips'
Plug 'honza/vim-snippets'
Plug 'prabirshrestha/asyncomplete.vim'
Plug 'prabirshrestha/asyncomplete-lsp.vim'

Plug 'wellle/tmux-complete.vim'

call plug#end()

map <C-n> :NERDTreeToggle<CR>
map U :UndotreeToggle<CR>
map <C-n> :NERDTreeToggle<CR>

map <leader>n :Files<CR>
map <leader>/ :Lines<CR>
map <C-/> :Rg<CR>
map <C-c> :Commits<CR>
map gt :Buffers<CR>

map gG :G<CR>
map <C-s> :VialHttp<CR>

set updatetime=100

let g:UltiSnipsExpandTrigger="<tab>"
let g:rainbow_active = 1
let g:indent_guides_enable_on_vim_startup = 1
let g:XkbSwitchEnabled = 1
let g:diminactive_use_syntax = 1
let g:qs_highlight_on_keys = ['f', 'F', 't', 'T']

autocmd VimEnter * DimInactiveOn

let g:diminactive_use_syntax = 1
let g:diminactive_use_colorcolumn = 0

function! s:on_lsp_buffer_enabled() abort
    setlocal omnifunc=lsp#complete
    setlocal signcolumn=yes
    if exists('+tagfunc') | setlocal tagfunc=lsp#tagfunc | endif
    nmap <buffer> gd <plug>(lsp-definition)
    nmap <buffer> g/ <plug>(lsp-document-symbol-search)
    nmap <buffer> g? <plug>(lsp-workspace-symbol-search)
    nmap <buffer> gr <plug>(lsp-references)
    nmap <buffer> gi <plug>(lsp-implementation)
    nmap <buffer> <leader>r <plug>(lsp-rename)
    nmap <buffer> <leader>i <plug>(lsp-next-diagnostic)
    nmap <buffer> <leader>I <plug>(lsp-previous-diagnostic)
    nmap <buffer> K <plug>(lsp-hover) <bar> :syntax on
    nmap <buffer> <leader>d <plug>(lsp-document-diagnostics)

    let g:lsp_format_sync_timeout = 1000
    autocmd! BufWritePre *.rs,*.go call execute('LspDocumentFormatSync')
endfunction

augroup lsp_install
    au!
    autocmd User lsp_buffer_enabled call s:on_lsp_buffer_enabled()
augroup END

let g:tmuxcomplete#asyncomplete_source_options = {
            \ 'name':      'tmuxcomplete',
            \ 'whitelist': ['*'],
            \ 'config': {
            \     'splitmode':      'words',
            \     'filter_prefix':   1,
            \     'show_incomplete': 1,
            \     'sort_candidates': 0,
            \     'scrollback':      0,
            \     'truncate':        0
            \     }
            \ }
inoremap <C-t> <C-x><C-u>
EOF


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

TMUX_CPU="#{cpu_bg_color} CPU: #{cpu_icon} #{cpu_percentage}"
TMUX_BAT="#{battery_status_bg} Batt: #{battery_icon} #{battery_percentage} #{battery_remain}"
TMUX_PREFIX="#{prefix_highlight}"

cat << EOF > ${USER_HOME}/.tmux.conf
set -g prefix C-a

set-option -g default-shell /bin/fish

bind C-a send-prefix
unbind C-b
set -sg escape-time 1
set -g base-index 1
setw -g pane-base-index 1
setw -g repeat-time 1000
bind r source-file ${USER_HOME}/.tmux.conf \; display 'Reloaded!

bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
bind c new-window -c      "#{pane_current_path}"

bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

bind -r C-h select-window -t :-
bind -r C-l select-window -t :+

bind -r H resize-pane -L 5
bind -r J resize-pane -D 5
bind -r K resize-pane -U 5
bind -r L resize-pane -R 5

set -g default-terminal "screen-256color"
set-window-option -g mode-keys vi

set -g @plugin "tmux-plugins/tpm"
set -g @plugin "tmux-plugins/tmux-resurrect"
set -g @plugin "tmux-plugins/tmux-cpu"
set -g @plugin "jaclu/tmux-power-zoom"
set -g @plugin "tmux-plugins/tmux-sidebar"
set -g @sidebar-tree-command "tree -C"

set -g @plugin "tmux-plugins/tmux-prefix-highlight"

set -g status-right "$TMUX_PREFIX | $TMUX_CPU | $TMUX_BAT | %a %h-%d %H:%M"
set -g status-right-length "150"

run "/etc/tmux/plugins/tpm/tpm"
EOF


#warpd
mkdir -p ${USER_HOME}/.config/warpd
cat << EOF > ${USER_HOME}/.config/warpd/config
activation_key: M-/
hint: C
hint2: c
exit: esc
drag: v
copy_and_exit: y
accelerator: space
buttons: Alt_L underscore Alt_R
history: colon
grid: g
screen: s
left: h
down: j
up: k
right: l
top: H
middle: M
bottom: L
start: 0
end: $
scroll_down: C-d
scroll_up: C-u
cursor_color: FF4500
cursor_size: 7
repeat_interval: 20
speed: 220
max_speed: 1600
acceleration: 700

hint_bgcolor: 00ff00
hint_fgcolor: 000000
hint_undo: u
scroll_speed: 300
scroll_max_speed: 9000
scroll_acceleration: 2600
indicator: topleft
indicator_color: 00ff00
indicator_size: 22
EOF


# bspwm
mkdir -p ${USER_HOME}/.config/bspwm
touch ${USER_HOME}/.config/bspwm/bspwmrc
chmod +x ${USER_HOME}/.config/bspwm/bspwmrc
cat << EOF > ${USER_HOME}/.config/bspwm/bspwmrc
#!/bin/sh
bspc monitor -d I II III IV V VI VII VIII IX X
bspc config border_width 2
bspc config borderless_monocle true
bspc config gapless_monocle true
bspc config focus_follows_pointer true
EOF

# sxhkd
mkdir -p ${USER_HOME}/.config/sxhkd
touch ${USER_HOME}/.config/sxhkd/sxhkdrc

cat << EOF > ${USER_HOME}/.config/sxhkd/sxhkdrc
#!/bin/sh

super + shift + {z,a}
 bspc node @/ -C {forward,backward}
super + Return
 st -e tmux

super + c
 CM_LAUNCHER=rofi clipmenu -i

super + Tab
 setxkbmap -option grp:alt_shift_toggle {dvorak, us},ru

Print
 flameshot gui

XF86AudioRaiseVolume
 amixer set Master 2%+
XF86AudioLowerVolume
 amixer set Master 2%-
XF86AudioMute
 amixer set Master toggle
XF86MonBrightnessUp
 xbacklight +5
XF86MonBrightnessDown
 xbacklight -5

super + n
 firefox
super + f
 bspc node -t ~fullscreen
super + shift + Return
 pkill -USR1 -x sxhkd
super + {j,k,l,p}
 bspc node -f {west,south,north,east}
super + d
 rofi -show run
super + shift + d
 rofi -show drun
super + shift + q
 bspc node -{c,k}
super + {_,shift + }{1-9,0}
 bspc {desktop -f,node -d} '^{1-9,10}'
super + r
 bspc node @/ -R 90
super + space
 bspc node -t {floating, tiled}
EOF


cat << EOF > /etc/doas.conf
permit ${USERNAME} as root
permit root as ${USERNAME}
permit nopass root
EOF


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
