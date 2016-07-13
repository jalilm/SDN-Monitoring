WHOAMI=`whoami`
mkdir /tmp/"$WHOAMI" > /dev/null 2>&1
complete -F _longopt -- -
complete -F _longopt -- --
complete -F _longopt -- less
alias -- -='less -Ci'
alias -- --='less -NCi'
alias ls='ls -F --color=auto'
alias lt='ls -Aglt'
alias ll='ls -al'
alias so='source'
alias ff='find . -name '
alias jobs='jobs -l'
alias cp='cp -r'
alias groups='groups "$WHOAMI"'
alias bg_jobs='ps aux | grep "$WHOAMI" | -'
alias sudo='sudo '
export PYTHONPATH=${PYTHONPATH}:~

kill_name() {
	sudo kill -9 `ps -aux | grep "$1" | cut -c8-14`
}

ko() {
        mv $1 /tmp/"$WHOAMI"
        rm -rf * > /dev/null 2>&1
        mv /tmp/"$WHOAMI"/$1 .
}

cdp() {
        pushd .
        cd $1
}

mkcd() {
        mkdir $1
        cd $1
}

notify () {
        curl --header 'Authorization: Bearer v1PpXrBY8fmOr11LOk2ujol7yJWuj97W0rujB348UiJhI' -X POST https://api.pushbullet.com/v2/pushes --header 'Content-Type: application/json' --data-binary '{"type": "note", "title": "Shell Notification", "body": "'$1'"}' > /dev/null 2>&1
}

calc () {
	awk "BEGIN { print $*}";
}
