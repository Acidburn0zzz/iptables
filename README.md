# iptables

Forked version of iptables with ClearOS changes applied

## Update usage
  Add __#kojibuild__ to commit message to automatically build

* git clone git://github.com/clearos/iptables.git
* cd iptables
* git checkout c7
* git remote add upstream git://git.centos.org/rpms/iptables.git
* git pull upstream c7
* git checkout clear7
* git merge --no-commit c7
* git commit
