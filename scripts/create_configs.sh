# I'm aware about heredocuments, but don't like them

RECREATION_DIR="$(mktemp -d)"
git clone https://github.com/readysloth/Workspace-recreation.git "$RECREATION_DIR"

SIJI_FONT_DIR="$(mktemp -d)"
git clone https://github.com/stark/siji "$SIJI_FONT_DIR"
pushd "$SIJI_FONT_DIR"
    ./install.sh -d ~/.fonts
popd

cd "$RECREATION_DIR"
# misc
echo 'net.ipv6.conf.all.disable_ipv6 = 1' >> /etc/sysctl.conf
mkdir -p ~/Images
cp -r "${RECREATION_DIR}/wallpapers" ~/Images


# vim plugin manager
curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# scripts
mkdir -p ~/.scripts
echo '#!/bin/bash'                                      > ~/.scripts/autochanging_wallpaper.sh
echo 'while true'                                      >> ~/.scripts/autochanging_wallpaper.sh
echo 'do'                                              >> ~/.scripts/autochanging_wallpaper.sh
echo '  feh --randomize --bg-fill ~/Images/wallpapers' >> ~/.scripts/autochanging_wallpaper.sh
echo '  sleep 1h'                                      >> ~/.scripts/autochanging_wallpaper.sh
echo 'done'                                            >> ~/.scripts/autochanging_wallpaper.sh


echo '#!/bin/bash'                                           > ~/.scripts/make_screenshot.sh
echo ''                                                     >> ~/.scripts/make_screenshot.sh
echo 'TEMP_DIR=$(mktemp -d)'                                >> ~/.scripts/make_screenshot.sh
echo 'pushd $TEMP_DIR'                                      >> ~/.scripts/make_screenshot.sh
echo '    scrot'                                            >> ~/.scripts/make_screenshot.sh
echo '    xclip -i -selection clipboard -t image/png *.png' >> ~/.scripts/make_screenshot.sh
echo 'popd'                                                 >> ~/.scripts/make_screenshot.sh

chmod +x ~/.scripts/autochanging_wallpaper.sh
chmod +x ~/.scripts/make_screenshot.sh

# bashrc
echo "bind 'set completion-ignore-case on'"       > ~/.bashrc
echo 'export EDITOR=vim'                         >> ~/.bashrc
#echo 'alias ls=exa'                              >> ~/.bashrc
#echo 'alias l=exa'                               >> ~/.bashrc
#echo 'alias cat=bat'                             >> ~/.bashrc
echo 'export PATH=$PATH:~/.cargo/bin:~/.scripts' >> ~/.bashrc

# fishrc
mkdir -p ~/.config/fish/
echo 'set -gx PATH $PATH ~/.cargo/bin ~/.scripts ~/.local/bin' >> ~/.config/fish/config.fish
echo 'set -gx EDITOR (command -v vim)'                         >> ~/.config/fish/config.fish

# Xinit
echo 'sxhkd &'                                           > ~/.xinitrc
echo "xset +fp $(echo ~/.fonts)"                        >> ~/.xinitrc
echo "xset fp rehash"                                   >> ~/.xinitrc
echo 'compton &'                                        >> ~/.xinitrc
echo 'clipmenud &'                                      >> ~/.xinitrc
echo 'pulseaudio --start --disallow-exit'               >> ~/.xinitrc
echo 'setxkbmap -option grp:alt_shift_toggle dvorak,ru' >> ~/.xinitrc
echo '~/.config/polybar/launch.sh --forest &'           >> ~/.xinitrc
echo '~/.scripts/autochanging_wallpaper.sh &'           >> ~/.xinitrc
echo 'exec bspwm'                                       >> ~/.xinitrc

# compton

echo "shadow = true;"                                                             >> ~/.config/compton.conf
echo "no-dnd-shadow = true;"                                                      >> ~/.config/compton.conf
echo "no-dock-shadow = true;"                                                     >> ~/.config/compton.conf
echo "clear-shadow = true;"                                                       >> ~/.config/compton.conf
echo "shadow-radius = 7;"                                                         >> ~/.config/compton.conf
echo "shadow-offset-x = -7;"                                                      >> ~/.config/compton.conf
echo "shadow-offset-y = -7;"                                                      >> ~/.config/compton.conf
echo "shadow-exclude = ["                                                         >> ~/.config/compton.conf
echo "	\"name = 'Notification'\","                                               >> ~/.config/compton.conf
echo "	\"class_g = 'Conky'\","                                                   >> ~/.config/compton.conf
echo "	\"class_g ?= 'Notify-osd'\","                                             >> ~/.config/compton.conf
echo "	\"class_g = 'Cairo-clock'\","                                             >> ~/.config/compton.conf
echo "	\"_GTK_FRAME_EXTENTS@:c\""                                                >> ~/.config/compton.conf
echo "];"                                                                         >> ~/.config/compton.conf
echo ""                                                                           >> ~/.config/compton.conf
echo "menu-opacity = 0.8;"                                                        >> ~/.config/compton.conf
echo "inactive-opacity = 0.9;"                                                    >> ~/.config/compton.conf
echo "frame-opacity = 0.7;"                                                       >> ~/.config/compton.conf
echo "inactive-opacity-override = true;"                                          >> ~/.config/compton.conf
echo "alpha-step = 0.06;"                                                         >> ~/.config/compton.conf
echo "blur-kern = \"3x3box\";"                                                    >> ~/.config/compton.conf
echo "blur-background-exclude = ["                                                >> ~/.config/compton.conf
echo "	\"window_type = 'dock'\","                                                >> ~/.config/compton.conf
echo "	\"window_type = 'desktop'\","                                             >> ~/.config/compton.conf
echo "	\"_GTK_FRAME_EXTENTS@:\""                                                 >> ~/.config/compton.conf
echo "];"                                                                         >> ~/.config/compton.conf
echo ""                                                                           >> ~/.config/compton.conf
echo "glx-copy-from-front = false;"                                               >> ~/.config/compton.conf
echo "glx-swap-method = \"undefined\";"                                           >> ~/.config/compton.conf
echo ""                                                                           >> ~/.config/compton.conf
echo "wintypes:"                                                                  >> ~/.config/compton.conf
echo "{"                                                                          >> ~/.config/compton.conf
echo "  tooltip = { fade = true; shadow = true; opacity = 0.75; focus = true; };" >> ~/.config/compton.conf
echo "};"                                                                         >> ~/.config/compton.conf


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
echo '""""""""""'         >> /etc/vim/vimrc
echo 'set number'         >> /etc/vim/vimrc
echo 'set relativenumber' >> /etc/vim/vimrc
echo                      >> /etc/vim/vimrc
echo 'set hlsearch'       >> /etc/vim/vimrc
echo 'set incsearch'      >> /etc/vim/vimrc
echo                      >> /etc/vim/vimrc
echo 'set wildmenu'       >> /etc/vim/vimrc
echo 'set nocompatible'   >> /etc/vim/vimrc
echo                      >> /etc/vim/vimrc
echo 'set tabstop=8'      >> /etc/vim/vimrc
echo 'set softtabstop=0'  >> /etc/vim/vimrc
echo 'set expandtab'      >> /etc/vim/vimrc
echo 'set shiftwidth=4'   >> /etc/vim/vimrc
echo 'set smarttab'       >> /etc/vim/vimrc
echo                      >> /etc/vim/vimrc
echo                      >> /etc/vim/vimrc
echo 'syntax on'          >> /etc/vim/vimrc
echo                      >> /etc/vim/vimrc

echo 'nnoremap <C-j> :m .+1<CR>'          >> /etc/vim/vimrc
echo 'nnoremap <C-k> :m .-2<CR>'          >> /etc/vim/vimrc
echo                                      >> /etc/vim/vimrc
echo 'inoremap <C-j> <ESC>:m .+1<CR>==gi' >> /etc/vim/vimrc
echo 'inoremap <C-k> <ESC>:m .-2<CR>==gi' >> /etc/vim/vimrc
echo                                      >> /etc/vim/vimrc
echo "vnoremap <C-j> :m '>1<CR>gv=gv"     >> /etc/vim/vimrc
echo "vnoremap <C-k> :m '<2<CR>gv=gv"     >> /etc/vim/vimrc
echo                                      >> /etc/vim/vimrc

echo "call plug#begin('~/.vim/plugged')"      >> /etc/vim/vimrc
echo                                          >> /etc/vim/vimrc
echo "Plug 'easymotion/vim-easymotion'"       >> /etc/vim/vimrc
echo "Plug 'godlygeek/tabular'"               >> /etc/vim/vimrc
echo "Plug 'luochen1990/rainbow'"             >> /etc/vim/vimrc
echo "Plug 'mbbill/undotree'"                 >> /etc/vim/vimrc
echo "Plug 'mkitt/tabline.vim'"               >> /etc/vim/vimrc
echo "Plug 'nathanaelkane/vim-indent-guides'" >> /etc/vim/vimrc
echo "Plug 'scrooloose/nerdtree'"             >> /etc/vim/vimrc
echo "Plug 'sheerun/vim-polyglot'"            >> /etc/vim/vimrc
echo "Plug 'tpope/vim-fugitive'"              >> /etc/vim/vimrc
echo "Plug 'tpope/vim-surround'"              >> /etc/vim/vimrc
echo "Plug 'chrisbra/csv.vim'"                >> /etc/vim/vimrc
echo "Plug 'lyokha/vim-xkbswitch'"            >> /etc/vim/vimrc
echo "Plug 'kovetskiy/sxhkd-vim'"             >> /etc/vim/vimrc
echo "Plug 'tpope/vim-repeat'"                >> /etc/vim/vimrc
echo "Plug 'junegunn/fzf.vim'"                >> /etc/vim/vimrc
echo "Plug 'blueyed/vim-diminactive'"         >> /etc/vim/vimrc
echo "Plug 'unblevable/quick-scope'"          >> /etc/vim/vimrc
echo "Plug 'wlangstroth/vim-racket'"          >> /etc/vim/vimrc
echo "Plug 'calebsmith/vim-lambdify'"         >> /etc/vim/vimrc
echo "Plug 'ntpeters/vim-better-whitespace'"  >> /etc/vim/vimrc
echo "Plug 'mhinz/vim-signify'"               >> /etc/vim/vimrc
echo "Plug 'wsdjeg/vim-fetch'"                >> /etc/vim/vimrc
echo "Plug 'Galicarnax/vim-regex-syntax'"     >> /etc/vim/vimrc
echo                                          >> /etc/vim/vimrc
echo "call plug#end()"                        >> /etc/vim/vimrc
echo                                          >> /etc/vim/vimrc
echo 'map <C-n> :NERDTreeToggle<CR>'                 >> /etc/vim/vimrc
echo 'map U :UndotreeToggle<CR>'                     >> /etc/vim/vimrc
echo 'map gG :G<CR>'                                 >> /etc/vim/vimrc
echo                                                 >> /etc/vim/vimrc
echo 'set updatetime=100'                            >> /etc/vim/vimrc
echo                                                 >> /etc/vim/vimrc
echo 'let g:rainbow_active = 1'                      >> /etc/vim/vimrc
echo 'let g:indent_guides_enable_on_vim_startup = 1' >> /etc/vim/vimrc
echo 'let g:XkbSwitchEnabled = 1'                    >> /etc/vim/vimrc
echo 'let g:diminactive_use_syntax = 1'              >> /etc/vim/vimrc
echo "let g:qs_highlight_on_keys = ['f', 'F', 't', 'T']" >> /etc/vim/vimrc
echo                                                 >> /etc/vim/vimrc
echo 'autocmd VimEnter * DimInactiveOn'              >> /etc/vim/vimrc
echo                                                 >> /etc/vim/vimrc
echo 'let g:diminactive_use_syntax = 1'              >> /etc/vim/vimrc
echo 'let g:diminactive_use_colorcolumn = 0'         >> /etc/vim/vimrc


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
vim +PlugInstall +qa


# tmux
git clone https://github.com/tmux-plugins/tpm /etc/tmux/plugins/tpm
echo 'set -g prefix C-a'                                       > ~/.tmux.conf
echo ''                                                       >> ~/.tmux.conf
echo 'set-option -g default-shell /bin/fish'                  >> ~/.tmux.conf
echo ''                                                       >> ~/.tmux.conf
echo 'bind C-a send-prefix'                                   >> ~/.tmux.conf
echo 'unbind C-b'                                             >> ~/.tmux.conf
echo 'set -sg escape-time 1'                                  >> ~/.tmux.conf
echo 'set -g base-index 1'                                    >> ~/.tmux.conf
echo 'setw -g pane-base-index 1'                              >> ~/.tmux.conf
echo 'setw -g repeat-time 1000'                               >> ~/.tmux.conf
echo 'bind r source-file ~/.tmux.conf \; display "Reloaded!"' >> ~/.tmux.conf
echo                                                          >> ~/.tmux.conf
echo 'bind | split-window -h -c "#{pane_current_path}"'       >> ~/.tmux.conf
echo 'bind - split-window -v -c "#{pane_current_path}"'       >> ~/.tmux.conf
echo 'bind c new-window -c      "#{pane_current_path}"'       >> ~/.tmux.conf
echo                                                          >> ~/.tmux.conf
echo 'bind h select-pane -L'                                  >> ~/.tmux.conf
echo 'bind j select-pane -D'                                  >> ~/.tmux.conf
echo 'bind k select-pane -U'                                  >> ~/.tmux.conf
echo 'bind l select-pane -R'                                  >> ~/.tmux.conf
echo                                                          >> ~/.tmux.conf
echo 'bind -r C-h select-window -t :-'                        >> ~/.tmux.conf
echo 'bind -r C-l select-window -t :+'                        >> ~/.tmux.conf
echo                                                          >> ~/.tmux.conf
echo 'bind -r H resize-pane -L 5'                             >> ~/.tmux.conf
echo 'bind -r J resize-pane -D 5'                             >> ~/.tmux.conf
echo 'bind -r K resize-pane -U 5'                             >> ~/.tmux.conf
echo 'bind -r L resize-pane -R 5'                             >> ~/.tmux.conf
echo                                                          >> ~/.tmux.conf
echo 'set -g default-terminal "screen-256color"'              >> ~/.tmux.conf
echo 'set-window-option -g mode-keys vi'                      >> ~/.tmux.conf
echo                                                          >> ~/.tmux.conf
echo 'set -g @plugin "tmux-plugins/tpm"'                      >> ~/.tmux.conf
echo                                                          >> ~/.tmux.conf
echo 'run "/etc/tmux/plugins/tpm/tpm"'                        >> ~/.tmux.conf


# polybar
mkdir -p ~/.config/polybar
touch ~/.config/polybar/config
/polybar_chooser.sh 11
sed -i '/font-1.*=.*"/ s/"[^"]*"/"Wuncon Siji:size=11"/' ~/.config/polybar/config.ini


#warpd
echo 'activation_key: M-/'             >> ~/.config/warpd/config
echo 'hint: C'                         >> ~/.config/warpd/config
echo 'hint2: c'                        >> ~/.config/warpd/config
echo 'exit: esc'                       >> ~/.config/warpd/config
echo 'drag: v'                         >> ~/.config/warpd/config
echo 'copy_and_exit: y'                >> ~/.config/warpd/config
echo 'accelerator: space'              >> ~/.config/warpd/config
echo 'buttons: Alt_L underscore Alt_R' >> ~/.config/warpd/config
echo 'history: colon'                  >> ~/.config/warpd/config
echo 'grid: g'                         >> ~/.config/warpd/config
echo 'screen: s'                       >> ~/.config/warpd/config
echo 'left: h'                         >> ~/.config/warpd/config
echo 'down: j'                         >> ~/.config/warpd/config
echo 'up: k'                           >> ~/.config/warpd/config
echo 'right: l'                        >> ~/.config/warpd/config
echo 'top: H'                          >> ~/.config/warpd/config
echo 'middle: M'                       >> ~/.config/warpd/config
echo 'bottom: L'                       >> ~/.config/warpd/config
echo 'start: 0'                        >> ~/.config/warpd/config
echo 'end: $'                          >> ~/.config/warpd/config
echo 'scroll_down: C-d'                >> ~/.config/warpd/config
echo 'scroll_up: C-u'                  >> ~/.config/warpd/config
echo 'cursor_color: FF4500'            >> ~/.config/warpd/config
echo 'cursor_size: 7'                  >> ~/.config/warpd/config
echo 'repeat_interval: 20'             >> ~/.config/warpd/config
echo 'speed: 220'                      >> ~/.config/warpd/config
echo 'max_speed: 1600'                 >> ~/.config/warpd/config
echo 'acceleration: 700'               >> ~/.config/warpd/config
echo                                   >> ~/.config/warpd/config
echo 'hint_bgcolor: 00ff00'            >> ~/.config/warpd/config
echo 'hint_fgcolor: 000000'            >> ~/.config/warpd/config
echo 'hint_undo: u'                    >> ~/.config/warpd/config
echo 'scroll_speed: 300'               >> ~/.config/warpd/config
echo 'scroll_max_speed: 9000'          >> ~/.config/warpd/config
echo 'scroll_acceleration: 2600'       >> ~/.config/warpd/config
echo 'indicator: topleft'              >> ~/.config/warpd/config
echo 'indicator_color: 00ff00'         >> ~/.config/warpd/config
echo 'indicator_size: 22'              >> ~/.config/warpd/config


# bspwm
mkdir -p ~/.config/bspwm
touch ~/.config/bspwm/bspwmrc
chmod +x ~/.config/bspwm/bspwmrc
echo '#!/bin/sh'                                      > ~/.config/bspwm/bspwmrc
echo 'bspc monitor -d I II III IV V VI VII VIII IX X' >> ~/.config/bspwm/bspwmrc
echo 'bspc config border_width 2'                     >> ~/.config/bspwm/bspwmrc
echo 'bspc config borderless_monocle true'            >> ~/.config/bspwm/bspwmrc
echo 'bspc config gapless_monocle true'               >> ~/.config/bspwm/bspwmrc
echo 'bspc config focus_follows_pointer true'         >> ~/.config/bspwm/bspwmrc

# sxhkd
mkdir -p ~/.config/sxhkd
touch ~/.config/sxhkd/sxhkdrc

echo '#!/bin/sh'                               > ~/.config/sxhkd/sxhkdrc

echo 'super + shift + {z,a}'                  >> ~/.config/sxhkd/sxhkdrc
echo ' bspc node @/ -C {forward,backward}'    >> ~/.config/sxhkd/sxhkdrc
echo 'super + Return'                         >> ~/.config/sxhkd/sxhkdrc
echo ' st -e tmux'                            >> ~/.config/sxhkd/sxhkdrc
echo                                          >> ~/.config/sxhkd/sxhkdrc
echo 'super + c'                              >> ~/.config/sxhkd/sxhkdrc
echo ' CM_LAUNCHER=rofi clipmenu -i'          >> ~/.config/sxhkd/sxhkdrc
echo                                          >> ~/.config/sxhkd/sxhkdrc
echo 'super + Tab'                            >> ~/.config/sxhkd/sxhkdrc
echo ' setxkbmap -option grp:alt_shift_toggle {dvorak, us},ru' >> ~/.config/sxhkd/sxhkdrc
echo                                          >> ~/.config/sxhkd/sxhkdrc
echo 'Print'                                  >> ~/.config/sxhkd/sxhkdrc
echo ' flameshot gui'                         >> ~/.config/sxhkd/sxhkdrc
echo                                          >> ~/.config/sxhkd/sxhkdrc
echo 'super + t'                                      >> ~/.config/sxhkd/sxhkdrc
echo ' bash ~/.config/polybar/scripts/colors_rofi.sh' >> ~/.config/sxhkd/sxhkdrc
echo                                                  >> ~/.config/sxhkd/sxhkdrc
echo 'XF86AudioRaiseVolume'      >> ~/.config/sxhkd/sxhkdrc
echo ' amixer set Master 2%+'    >> ~/.config/sxhkd/sxhkdrc
echo 'XF86AudioLowerVolume'      >> ~/.config/sxhkd/sxhkdrc
echo ' amixer set Master 2%-'    >> ~/.config/sxhkd/sxhkdrc
echo 'XF86AudioMute'             >> ~/.config/sxhkd/sxhkdrc
echo ' amixer set Master toggle' >> ~/.config/sxhkd/sxhkdrc
echo 'XF86MonBrightnessUp'       >> ~/.config/sxhkd/sxhkdrc
echo ' xbacklight +5'            >> ~/.config/sxhkd/sxhkdrc
echo 'XF86MonBrightnessDown'     >> ~/.config/sxhkd/sxhkdrc
echo ' xbacklight -5'            >> ~/.config/sxhkd/sxhkdrc
echo                                          >> ~/.config/sxhkd/sxhkdrc
echo 'super + n'                              >> ~/.config/sxhkd/sxhkdrc
echo ' firefox'                               >> ~/.config/sxhkd/sxhkdrc
echo 'super + f'                              >> ~/.config/sxhkd/sxhkdrc
echo ' bspc node -t ~fullscreen'              >> ~/.config/sxhkd/sxhkdrc
echo 'super + shift + Return'                 >> ~/.config/sxhkd/sxhkdrc
echo ' pkill -USR1 -x sxhkd'                  >> ~/.config/sxhkd/sxhkdrc
echo 'super + {j,k,j,p}'                      >> ~/.config/sxhkd/sxhkdrc
echo ' bspc node -f {west,south,north,east}'  >> ~/.config/sxhkd/sxhkdrc
echo 'super + d'                              >> ~/.config/sxhkd/sxhkdrc
echo ' rofi -show run'                        >> ~/.config/sxhkd/sxhkdrc
echo 'super + shift + d'                      >> ~/.config/sxhkd/sxhkdrc
echo ' rofi -show drun'                       >> ~/.config/sxhkd/sxhkdrc
echo 'super + shift + q'                      >> ~/.config/sxhkd/sxhkdrc
echo ' bspc node -{c,k}'                      >> ~/.config/sxhkd/sxhkdrc
echo 'super + {_,shift + }{1-9,0}'            >> ~/.config/sxhkd/sxhkdrc
echo " bspc {desktop -f,node -d} '^{1-9,10}'" >> ~/.config/sxhkd/sxhkdrc
echo 'super + r'                              >> ~/.config/sxhkd/sxhkdrc
echo ' bspc node @/ -R 90'                    >> ~/.config/sxhkd/sxhkdrc
echo 'super + space'                          >> ~/.config/sxhkd/sxhkdrc
echo ' bspc node -t {floating, tiled}'        >> ~/.config/sxhkd/sxhkdrc



git config --global core.editor vim
cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime
