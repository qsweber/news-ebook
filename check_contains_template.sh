TERM=xterm-256color git branch --contains $(git ls-remote git://github.com/qsweber/service-template.git | grep refs/heads/master | cut -f 1)