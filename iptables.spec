# Important for version updates: Fix virtual provides for base libaries

Name: iptables
Summary: Tools for managing Linux kernel packet filtering capabilities
Version: 1.4.7
Release: 16%{?dist}
Source: http://www.netfilter.org/projects/iptables/files/%{name}-%{version}.tar.bz2
Source1: iptables.init
Source2: iptables-config
Source3: libxt_AUDIT.man
Patch5: iptables-1.4.5-cloexec.patch
Patch6: iptables-1.4.7-xt_CHECKSUM.patch
Patch7: iptables-1.4.7-tproxy.patch
Patch8: iptables-1.4.7-xt_AUDIT_v2.patch
Patch9: iptables-1.4.7-opt_parser_v2.patch
Patch10: iptables-1.4.7-chain_maxnamelen.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=845435 "--queue-bypass" backport
Patch11: iptables-1.4.7-xt_NFQUEUE.patch
Patch12: iptables-1.4.7-rhbz_983198.patch
Patch13: iptables-1.4.7-ipXt_set.patch
Patch14: iptables-1.4.7-fix_dccp_types_print.patch
Patch15: iptables-1.4.7-check_option.patch
Group: System Environment/Base
URL: http://www.netfilter.org/
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
License: GPLv2
BuildRequires: libselinux-devel
BuildRequires: kernel-headers
Conflicts: kernel < 2.4.20
Requires: policycoreutils
Requires(preun): %{_sbindir}/alternatives chkconfig
Requires(post): %{_sbindir}/alternatives chkconfig
Requires(postun): %{_sbindir}/alternatives
# Virtual base library provides for library file requires
Provides: /%{_lib}/libiptc.so.0
Provides: /%{_lib}/libip4tc.so.0
Provides: /%{_lib}/libip6tc.so.0
Provides: /%{_lib}/libipq.so.0
Provides: /%{_lib}/libxtables.so.4

%description
The iptables utility controls the network packet filtering code in the
Linux kernel. If you need to set up firewalls and/or IP masquerading,
you should install this package.

%package ipv6
Summary: IPv6 support for iptables
Group: System Environment/Base
Requires: %{name} = %{version}-%{release}
Requires(post): chkconfig
Requires(preun): chkconfig

%description ipv6
The iptables package contains IPv6 (the next version of the IP
protocol) support for iptables. Iptables controls the Linux kernel
network packet filtering code, allowing you to set up firewalls and IP
masquerading. 

Install iptables-ipv6 if you need to set up firewalling for your
network and you are using ipv6.

%package devel
Summary: Development package for iptables
Group: System Environment/Base
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig

%description devel
iptables development headers and libraries.

The iptc interface is upstream marked as not public. The interface is not 
stable and may change with every new version. It is therefore unsupported.

%prep
%setup -q
%patch5 -p1 -b .cloexec
%patch6 -p1 -b .xt_CHECKSUM
%patch7 -p1 -b .tproxy
%patch8 -p1 -b .xt_AUDIT_v2
%patch9 -p1 -b .opt_parser_v2
%patch10 -p1 -b .chain_maxnamelen
%patch11 -p1 -b .xt_NFQUEUE
%patch12 -p1 -b .rhbz_983198
%patch13 -p1 -b .ipXt_set
%patch14 -p1 -b .fix_dccp_types_print
%patch15 -p1 -b .check_option
cp %{SOURCE3} extensions/

%build
#
# Packges other than 1.4.7 need to add this to the configure call:
# --with-xtlibdir=/%{_lib}/xtables-%{version}
#
CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing" \
./configure --enable-devel --enable-libipq --bindir=/bin --sbindir=/sbin --sysconfdir=/etc --libdir=/%{_lib} --libexecdir=/%{_lib} --mandir=%{_mandir} --includedir=%{_includedir} --with-kernel=/usr --with-kbuild=/usr --with-ksource=/usr

# do not use rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make

%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot} 
# remove la file(s)
rm -f %{buildroot}/%{_lib}/*.la

# install ip*tables.h header files
install -m 644 include/ip*tables.h %{buildroot}%{_includedir}/
install -d -m 755 %{buildroot}%{_includedir}/iptables
install -m 644 include/iptables/internal.h %{buildroot}%{_includedir}/iptables/

# install ipulog header file
install -d -m 755 %{buildroot}%{_includedir}/libipulog/
install -m 644 include/libipulog/*.h %{buildroot}%{_includedir}/libipulog/

# create symlinks for devel so libs
install -d -m 755 %{buildroot}%{_libdir}
for i in %{buildroot}/%{_lib}/*.so; do
    ln -s ../../%{_lib}/${i##*/} %{buildroot}%{_libdir}/${i##*/}
done

# move pkgconfig to %{_libdir}
mv %{buildroot}/%{_lib}/pkgconfig %{buildroot}/%{_libdir}/

# install init scripts and configuration files
install -d -m 755 %{buildroot}/etc/rc.d/init.d
install -c -m 755 %{SOURCE1} %{buildroot}/etc/rc.d/init.d/iptables
sed -e 's;iptables;ip6tables;g' -e 's;IPTABLES;IP6TABLES;g' < %{SOURCE1} > ip6tables.init
install -c -m 755 ip6tables.init %{buildroot}/etc/rc.d/init.d/ip6tables
install -d -m 755 %{buildroot}/etc/sysconfig
install -c -m 755 %{SOURCE2} %{buildroot}/etc/sysconfig/iptables-config
sed -e 's;iptables;ip6tables;g' -e 's;IPTABLES;IP6TABLES;g' < %{SOURCE2} > ip6tables-config
install -c -m 755 ip6tables-config %{buildroot}/etc/sysconfig/ip6tables-config

# rename files for alternative usage
cd %{buildroot}
for i in sbin/ip*tables sbin/ip*tables-multi sbin/ip*tables-restore sbin/ip*tables-save bin/iptables-xml; do
    mv $i $i-%{version}
done
cd %{buildroot}%{_mandir}/man8/
for i in *.8*; do
    mv $i ${i%%.8*}-%{version}.8${i##*.8}
done
cd %{buildroot}/%{_lib}
rm libiptc.so.0 libip4tc.so.0 libip6tc.so.0 libipq.so.0 libxtables.so.4
for i in lib*.so.*; do
    mv $i $i-%{version}
done
ln -s libiptc.so.0.0.0-%{version} libiptc.so.0-%{version}
ln -s libip4tc.so.0.0.0-%{version} libip4tc.so.0-%{version}
ln -s libip6tc.so.0.0.0-%{version} libip6tc.so.0-%{version}
ln -s libipq.so.0.0.0-%{version} libipq.so.0-%{version}
ln -s libxtables.so.4.0.0-%{version} libxtables.so.4-%{version}

%clean
rm -rf %{buildroot}

%pre
# if /%{_lib}/xtables is a symlink, remove it.
if [ $1 -gt 1 ]; then
   [ -h /%{_lib}/xtables ] && rm /%{_lib}/xtables || :
fi

%post
/sbin/ldconfig
/sbin/chkconfig --add iptables
#
# Packges other than 1.4.7 need to add this to the alternatives call:
# --slave /%{_lib}/xtables lib-xtables.%{_arch} /%{_lib}/xtables-%{version} \
#
%{_sbindir}/alternatives --install /sbin/iptables iptables.%{_arch} /sbin/iptables-%{version} 90 \
        --slave /sbin/iptables-multi sbin-iptables-multi.%{_arch} /sbin/iptables-multi-%{version} \
        --slave /sbin/iptables-restore sbin-iptables-restore.%{_arch}  /sbin/iptables-restore-%{version} \
        --slave /sbin/iptables-save sbin-iptables-save.%{_arch} /sbin/iptables-save-%{version} \
        --slave /bin/iptables-xml bin-iptables-xml.%{_arch} /bin/iptables-xml-%{version} \
        --slave %{_mandir}/man8/iptables-restore.8.gz man-iptables-restore.%{_arch} %{_mandir}/man8/iptables-restore-%{version}.8.gz \
        --slave %{_mandir}/man8/iptables-save.8.gz man-iptables-save.%{_arch} %{_mandir}/man8/iptables-save-%{version}.8.gz \
        --slave %{_mandir}/man8/iptables-xml.8.gz man-iptables-xml.%{_arch} %{_mandir}/man8/iptables-xml-%{version}.8.gz \
        --slave %{_mandir}/man8/iptables.8.gz man-iptables.%{_arch} %{_mandir}/man8/iptables-%{version}.8.gz \
        --slave /%{_lib}/libip4tc.so.0 libip4tc0.%{_arch} /%{_lib}/libip4tc.so.0-%{version} \
        --slave /%{_lib}/libip4tc.so.0.0.0 libip4tc000.%{_arch} /%{_lib}/libip4tc.so.0.0.0-%{version} \
        --slave /%{_lib}/libip6tc.so.0 libip6tc0.%{_arch} /%{_lib}/libip6tc.so.0-%{version} \
        --slave /%{_lib}/libip6tc.so.0.0.0 libip6tc000.%{_arch} /%{_lib}/libip6tc.so.0.0.0-%{version} \
        --slave /%{_lib}/libiptc.so.0 libiptc0.%{_arch} /%{_lib}/libiptc.so.0-%{version} \
        --slave /%{_lib}/libiptc.so.0.0.0 libiptc000.%{_arch} /%{_lib}/libiptc.so.0.0.0-%{version} \
        --slave /%{_lib}/libipq.so.0 libipq0.%{_arch} /%{_lib}/libipq.so.0-%{version} \
        --slave /%{_lib}/libipq.so.0.0.0 libipq000.%{_arch} /%{_lib}/libipq.so.0.0.0-%{version} \
        --slave /%{_lib}/libxtables.so.4 libxtables4.%{_arch} /%{_lib}/libxtables.so.4-%{version} \
        --slave /%{_lib}/libxtables.so.4.0.0 libxtables400.%{_arch} /%{_lib}/libxtables.so.4.0.0-%{version} \
        --initscript iptables

%postun
/sbin/ldconfig
if [ "$1" -ge "1" ]; then
        iptables=`readlink %{_sysconfdir}/alternatives/iptables.%{_arch}`
        if [ "$iptables" == "/sbin/iptables-%{version}" ]; then
                %{_sbindir}/alternatives --set iptables.%{_arch} /sbin/iptables-%{version}
        fi
fi
exit 0

%preun
if [ "$1" = 0 ]; then
        /sbin/chkconfig --del iptables
        %{_sbindir}/alternatives --remove iptables.%{_arch} /sbin/iptables-%{version} || :
fi

%triggerpostun -- iptables < 1.4.7-7
iptables=`readlink %{_sysconfdir}/alternatives/iptables.%{_arch}`
if [ -z "$iptables" -o "$iptables" == "/sbin/iptables-%{version}" ]; then
        %{_sbindir}/alternatives --set iptables.%{_arch} /sbin/iptables-%{version}
fi

%triggerpostun -- iptables < 1.4.7-15
# copy plugins file over from the old package to the new one
if [ -d /%{_lib}/xtables-1.4.7 ]; then
	for i in /%{_lib}/xtables-1.4.7/*.so; do
		cp -an "$i" /%{_lib}/xtables/
	done
fi

%post ipv6
/sbin/chkconfig --add ip6tables
%{_sbindir}/alternatives --install /sbin/ip6tables ip6tables.%{_arch} /sbin/ip6tables-%{version} 90 \
        --slave /sbin/ip6tables-multi sbin-ip6tables-multi.%{_arch} /sbin/ip6tables-multi-%{version} \
        --slave /sbin/ip6tables-restore sbin-ip6tables-restore.%{_arch}  /sbin/ip6tables-restore-%{version} \
        --slave /sbin/ip6tables-save sbin-ip6tables-save.%{_arch} /sbin/ip6tables-save-%{version} \
        --slave %{_mandir}/man8/ip6tables-restore.8.gz man-ip6tables-restore.%{_arch} %{_mandir}/man8/ip6tables-restore-%{version}.8.gz \
        --slave %{_mandir}/man8/ip6tables-save.8.gz man-ip6tables-save.%{_arch} %{_mandir}/man8/ip6tables-save-%{version}.8.gz \
        --slave %{_mandir}/man8/ip6tables.8.gz man-ip6tables.%{_arch} %{_mandir}/man8/ip6tables-%{version}.8.gz \
        --initscript ip6tables

%postun ipv6
if [ "$1" -ge "1" ]; then
        ip6tables=`readlink %{_sysconfdir}/alternatives/ip6tables.%{_arch}`
        if [ "$ip6tables" == "/sbin/ip6tables-%{version}" ]; then
                %{_sbindir}/alternatives --set ip6tables.%{_arch} /sbin/ip6tables-%{version}
        fi
fi
exit 0

%preun ipv6
if [ "$1" = 0 ]; then
        /sbin/chkconfig --del ip6tables
        %{_sbindir}/alternatives --remove ip6tables.%{_arch} /sbin/ip6tables-%{version} || :
fi

%triggerpostun ipv6 -- iptables-ipv6 < 1.4.7-7
ip6tables=`readlink %{_sysconfdir}/alternatives/ip6tables.%{_arch}`
if [ -z "$ip6tables" -o "$ip6tables" == "/sbin/ip6tables-%{version}" ]; then
        %{_sbindir}/alternatives --set ip6tables.%{_arch} /sbin/ip6tables-%{version}
fi

%files
%defattr(-,root,root)
%doc COPYING INSTALL INCOMPATIBILITIES
%attr(0755,root,root) /etc/rc.d/init.d/iptables
%config(noreplace) %attr(0600,root,root) /etc/sysconfig/iptables-config
/sbin/iptables*-%{version}
/bin/iptables-xml-%{version}
%{_mandir}/man8/iptables*-%{version}.8*
#
# Packges other than 1.4.7 need to change these lines:
# -%dir /%{_lib}/xtables
# -/%{_lib}/xtables/libipt*
# -/%{_lib}/xtables/libxt*
# +%dir /%{_lib}/xtables-%{version}
# +/%{_lib}/xtables-%{version}/libipt*
# +/%{_lib}/xtables-%{version}/libxt*
#
%dir /%{_lib}/xtables
/%{_lib}/xtables/libipt*
/%{_lib}/xtables/libxt*
/%{_lib}/libip*tc.so.*-%{version}
/%{_lib}/libipq.so.*-%{version}
/%{_lib}/libxtables.so.*-%{version}

%files ipv6
%defattr(-,root,root)
%attr(0755,root,root) /etc/rc.d/init.d/ip6tables
%config(noreplace) %attr(0600,root,root) /etc/sysconfig/ip6tables-config
/sbin/ip6tables*-%{version}
%{_mandir}/man8/ip6tables*-%{version}.8*
#
# Packges other than 1.4.7 need to change these lines:
# -/%{_lib}/xtables/libip6t*
# +/%{_lib}/xtables-%{version}/libip6t*
#
/%{_lib}/xtables/libip6t*

%files devel
%defattr(-,root,root)
%dir %{_includedir}/iptables
%{_includedir}/iptables/*.h
%{_includedir}/*.h
%dir %{_includedir}/libiptc
%{_includedir}/libiptc/*.h
%dir %{_includedir}/libipulog
%{_includedir}/libipulog/*.h
%{_mandir}/man3/*
/%{_lib}/libip*tc.so
/%{_lib}/libipq.so
/%{_lib}/libxtables.so
%{_libdir}/libip*tc.so
%{_libdir}/libipq.so
%{_libdir}/libxtables.so
%{_libdir}/pkgconfig/libiptc.pc
%{_libdir}/pkgconfig/xtables.pc

%changelog
* Tue Mar 26 2015 Thomas Woerner <twoerner@redhat.com> 1.4.7-16
- Fixed ressource leak in libiptc found by coverity (rhbz#1088361)
- Copy custom plugins also for releases up to 14 (rhbz#1088400)

* Tue Mar  3 2015 Thomas Woerner <twoerner@redhat.com> 1.4.7-15
- Add message for init script error returns (rhbz#1081191)
- Fix rule deletion of ipset matches (rhbz#1081422)
- Add space after dccp types (rhbz#1084974)
- Add -C option to check for existing rules (rhbz#1088361)
- Copy custom plugins for updates from iptables < 1.4.7-10 (rhbz#1088400)
- Enable the IPv6 set target (rhbz#1161330)

* Thu Aug 28 2014 Thomas Woerner <twoerner@redhat.com> 1.4.7-14
- fixed inversion issue with set match (rhbz#1132403)

* Tue Aug 26 2014 Thomas Woerner <twoerner@redhat.com> 1.4.7-13
- fixed ip6tables ipset dst error (rhbz#1132403)

* Mon Jun 16 2014 Thomas Woerner <twoerner@redhat.com> 1.4.7-12
- added ip6t_set (rhbz#1033270)
- do not block uninstall on a failing alternatives --remove call in preun
  (rhbz#1059214) (rhbz#1070123)

* Tue Sep 17 2013 Thomas Woerner <twoerner@redhat.com> 1.4.7-11
- fixed shutdown hang if root filesystem is network based (rhbz#1007632)
  Thanks to Rodrigo A B Freire for the patch

* Wed Aug 14 2013 Thomas Woerner <twoerner@redhat.com> 1.4.7-10
- New reload action for ip*tables services (rhbz#928812)
  It tries to reload the firewall rules from /etc/sysconfig/ip*tables. If this
  failes, it does not load the fallbacks and the old firewall rules are still
  there.
- Use /lib*/xtables without version and not linked by alternatives again for 
  compatibility to older versions (rhbz#924362)
  The symlink for /lib*/xtables with the previous version will be cleaned up
  in a pre script.
- Backport of --queue-bypass (rhbz#845435)
  Thanks to Florian Westphal and kay
- Make ip*tables-save consistent to man page (rhbz#983198)

* Wed Oct 31 2012 Thomas Woerner <twoerner@redhat.com> 1.4.7-9
- make alternatives names arch dependant for multilib (rhbz#860148)
- added virtual provides for base libraries to be able to resolve library file requires

* Tue Oct  9 2012 Thomas Woerner <twoerner@redhat.com> 1.4.7-8
- do not use alternatives for the init scripts (rhbz#860148)

* Tue Sep 18 2012 Thomas Woerner <twoerner@redhat.com> 1.4.7-7
- Use alternatives to support other iptables versions for MRG kernels
  (rhbz#747068)
- Restore sysctl values on service restart (rhbz#800208)
- Added fallback support in case of error in service start (rhbz#808272)
- Added AUDIT targets to to man pages (rhbz#809108)
- Fixed maximum chain name length (rhbz#821441)
- Added missing dependency for poliycoreutils package (rhbz#836286)

* Fri Feb  3 2012 Thomas Woerner <twoerner@redhat.com> 1.4.7-6
- reverted upstream patches, because they are breaking the ABI
- created new patch based on upstream but without ABI break (rhbz#725879)

* Fri Nov 11 2011 Thomas Woerner <twoerner@redhat.com> 1.4.7-5
- fixed option parser problem (mark matches with mark options) (rhbz#725879)
  based on upstream commits:
    600f38db82548a683775fd89b6e136673e924097
    59e8114c6792242e80785f4461d5e663fb9a3d64
    d3b2e391e3b944581e20e216af76339cc87d0590
    2d68ae7ce6e40e3977ee11a57296cf76801ae320
    1dc27393b7ba401e6228a5ee2472a6eb72836c43
    1e128bd804b676ee91beca48312de9b251845d09
    fa503ad59f73d20d85f4cdf53324a01d2ad8591e

* Fri Jan  7 2011 Thomas Woerner <twoerner@redhat.com> 1.4.7-4
- added IPv6 transparent proxy support (rhbz#590186)
- added auditing support (rhbz#642393)
  Thanks to Thomas Graf for the patch
- init: restore context for save and use /etc/sysconfig for temps (rhbz#644273)

* Tue Jul 13 2010 Thomas Woerner <twoerner@redhat.com> 1.4.7-3
- added xt_CHECKSUM patch from Michael S. Tsirkin (rhbz#612587)

* Tue Jun 29 2010 Thomas Woerner <twoerner@redhat.com> 1.4.7-2
- fixed initscript to be LSB compliant (rhbz#593228)
  - added euid 0 check
  - reload returns 3 (unimplemented feature)

* Wed Mar 24 2010 Thomas Woerner <twoerner@redhat.com> 1.4.7-1
- rebase to version 1.4.7:
  - libip4tc: Add static qualifier to dump_entry()
  - libipq: build as shared library
  - recent: reorder cases in code (cosmetic cleanup)
  - several man page and documentation fixes
  - policy: fix error message showing wrong option
  - includes: header updates
  - Lift restrictions on interface names
- fixed license and moved iptables-xml into base package according to review
- added default values for IPTABLES_STATUS_VERBOSE and
  IPTABLES_STATUS_LINENUMBERS in init script

* Fri Feb 26 2010 Thomas Woerner <twoerner@redhat.com> 1.4.6-4
- changed license to GPLv2
- removed execution bits from iptables.init

* Fri Feb 26 2010 Thomas Woerner <twoerner@redhat.com> 1.4.6-3
- fixes according to review:
- fixed license
- moved /bin/iptables-xml to iptables main package fixes dangling symlink in
  ipv6 sub-package
- added missing lsb keywords Required-Start and Required-Stop to init script

* Wed Jan 27 2010 Thomas Woerner <twoerner@redhat.com> 1.4.6-2
- moved libip*tc and libxtables libs to /lib[64], added symlinks for .so libs
  to /usr/lib[64] for compatibility (rhbz#558796)

* Wed Jan 13 2010 Thomas Woerner <twoerner@redhat.com> 1.4.6-1
- new version 1.4.6 with support for all new features of 2.6.32
  - several man page fixes
  - Support for nommu arches
  - realm: remove static initializations
  - libiptc: remove unused functions
  - libiptc: avoid strict-aliasing warnings
  - iprange: do accept non-ranges for xt_iprange v1
  - iprange: warn on reverse range
  - iprange: roll address parsing into a loop
  - iprange: do accept non-ranges for xt_iprange v1 (log)
  - iprange: warn on reverse range (log)
  - libiptc: fix wrong maptype of base chain counters on restore
  - iptables: fix undersized deletion mask creation
  - style: reduce indent in xtables_check_inverse
  - libxtables: hand argv to xtables_check_inverse
  - iptables/extensions: make bundled options work again
  - CONNMARK: print mark rules with mask 0xffffffff as set instead of xset
  - iptables: take masks into consideration for replace command
  - doc: explain experienced --hitcount limit
  - doc: name resolution clarification
  - iptables: expose option to zero packet/byte counters for a specific rule
  - build: restore --disable-ipv6 functionality on system w/o v6 headers
  - MARK: print mark rules with mask 0xffffffff as --set-mark instead of --set-xmark
  - DNAT: fix incorrect check during parsing
  - extensions: add osf extension
  - conntrack: fix --expires parsing

* Thu Dec 17 2009 Thomas Woerner <twoerner@redhat.com> 1.4.5-2
- dropped nf_ext_init remains from cloexec patch

* Thu Sep 17 2009 Thomas Woerner <twoerner@redhat.com> 1.4.5-1
- new version 1.4.5 with support for all new features of 2.6.31
  - libxt_NFQUEUE: add new v1 version with queue-balance option
  - xt_conntrack: revision 2 for enlarged state_mask member
  - libxt_helper: fix invalid passed option to check_inverse
  - libiptc: split v4 and v6
  - extensions: collapse registration structures
  - iptables: allow for parse-less extensions
  - iptables: allow for help-less extensions
  - extensions: remove empty help and parse functions
  - xtables: add multi-registration functions
  - extensions: collapse data variables to use multi-reg calls
  - xtables: warn of missing version identifier in extensions
  - multi binary: allow subcommand via argv[1]
  - iptables: accept multiple IP address specifications for -s, -d
  - several build fixes
  - several man page fixes
- fixed two leaked file descriptors on sockets (rhbz#521397)

* Mon Aug 24 2009 Thomas Woerner <twoerner@redhat.com> 1.4.4-1
- new version 1.4.4 with support for all new features of 2.6.30
  - several man page fixes
  - iptables: replace open-coded sizeof by ARRAY_SIZE
  - libip6t_policy: remove redundant functions
  - policy: use direct xt_policy_info instead of ipt/ip6t
  - policy: merge ipv6 and ipv4 variant
  - extensions: add `cluster' match support
  - extensions: add const qualifiers in print/save functions
  - extensions: use NFPROTO_UNSPEC for .family field
  - extensions: remove redundant casts
  - iptables: close open file descriptors
  - fix segfault if incorrect protocol name is used
  - replace open-coded sizeof by ARRAY_SIZE
  - do not include v4-only modules in ip6tables manpage
  - use direct xt_policy_info instead of ipt/ip6t
  - xtables: fix segfault if incorrect protocol name is used
  - libxt_connlimit: initialize v6_mask
  - SNAT/DNAT: add support for persistent multi-range NAT mappings

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Apr 15 2009 Thomas Woerner <twoerner@redhat.com> 1.4.3.2-1
- new version 1.4.3.2
- also install iptables/internal.h, needed for iptables.h and ip6tables.h

* Mon Mar 30 2009 Thomas Woerner <twoerner@redhat.com> 1.4.3.1-1
- new version 1.4.3.1
  - libiptc is now shared
  - supports all new features of the 2.6.29 kernel
- dropped typo_latter patch

* Thu Mar  5 2009 Thomas Woerner <twoerner@redhat.com> 1.4.2-3
- still more review fixes (rhbz#225906)
  - consistent macro usage
  - use sed instead of perl for rpath removal
  - use standard RPM CFLAGS, but also -fno-strict-aliasing (needed for libiptc*)

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 20 2009 Thomas Woerner <twoerner@redhat.com> 1.4.2-1
- new version 1.4.2
- removed TOS value mask patch (upstream)
- more review fixes (rhbz#225906)
- install all header files (rhbz#462207)
- dropped nf_ext_init (rhbz#472548)

* Tue Jul 22 2008 Thomas Woerner <twoerner@redhat.com> 1.4.1.1-2
- fixed TOS value mask problem (rhbz#456244) (upstream patch)
- two more cloexec fixes

* Tue Jul  1 2008 Thomas Woerner <twoerner@redhat.com> 1.4.1.1-1
- upstream bug fix release 1.4.1.1
- dropped extra patch for 1.4.1 - not needed anymore

* Tue Jun 10 2008 Thomas Woerner <twoerner@redhat.com> 1.4.1-1
- new version 1.4.1 with new build environment
- additional ipv6 network mask patch from Jan Engelhardt
- spec file cleanup
- removed old patches

* Fri Jun  6 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.4.0-5
- use normal kernel headers, not linux/compiler.h
- change BuildRequires: kernel-devel to kernel-headers
- We need to do this to be able to build for both sparcv9 and sparc64 
  (there is no kernel-devel.sparcv9)

* Thu Mar 20 2008 Thomas Woerner <twoerner@redhat.com> 1.4.0-4
- use O_CLOEXEC for all opened files in all applications (rhbz#438189)

* Mon Mar  3 2008 Thomas Woerner <twoerner@redhat.com> 1.4.0-3
- use the kernel headers from the build tree for iptables for now to be able to 
  compile this package, but this makes the package more kernel dependant
- use s6_addr32 instead of in6_u.u6_addr32

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.4.0-2
- Autorebuild for GCC 4.3

* Mon Feb 11 2008 Thomas Woerner <twoerner@redhat.com> 1.4.0-1
- new version 1.4.0
- fixed condrestart (rhbz#428148)
- report the module in rmmod_r if there is an error
- use nf_ext_init instead of my_init for extension constructors

* Mon Nov  5 2007 Thomas Woerner <twoerner@redhat.com> 1.3.8-6
- fixed leaked file descriptor before fork/exec (rhbz#312191)
- blacklisting is not working, use "install X /bin/(true|false)" test instead
- return private exit code 150 for disabled ipv6 support
- use script name for output messages

* Tue Oct 16 2007 Thomas Woerner <twoerner@redhat.com> 1.3.8-5
- fixed error code for stopping a already stopped firewall (rhbz#321751)
- moved blacklist test into start

* Wed Sep 26 2007 Thomas Woerner <twoerner@redhat.com> 1.3.8-4.1
- do not start ip6tables if ipv6 is blacklisted (rhbz#236888)
- use simpler fix for (rhbz#295611)
  Thanks to Linus Torvalds for the patch.

* Mon Sep 24 2007 Thomas Woerner <twoerner@redhat.com> 1.3.8-4
- fixed IPv6 reject type (rhbz#295181)
- fixed init script: start, stop and status
- support netfilter compiled into kernel in init script (rhbz#295611)
- dropped inversion for limit modules from man pages (rhbz#220780)
- fixed typo in ip6tables man page (rhbz#236185)

* Wed Sep 19 2007 Thomas Woerner <twoerner@redhat.com> 1.3.8-3
- do not depend on local_fs in lsb header - this delayes start after network
- fixed exit code for initscript usage

* Mon Sep 17 2007 Thomas Woerner <twoerner@redhat.com> 1.3.8-2.1
- do not use lock file for condrestart test

* Thu Aug 23 2007 Thomas Woerner <twoerner@redhat.com> 1.3.8-2
- fixed initscript for LSB conformance (rhbz#246953, rhbz#242459)
- provide iptc interface again, but unsupported (rhbz#216733)
- compile all extension, which are supported by the kernel-headers package
- review fixes (rhbz#225906)

* Tue Jul 31 2007 Thomas Woerner <twoerner@redhat.com>
- reverted ipv6 fix, because it disables the ipv6 at all (rhbz#236888)

* Fri Jul 13 2007 Steve Conklin <sconklin@redhat.com> - 1.3.8-1
- New version 1.3.8

* Mon Apr 23 2007 Jeremy Katz <katzj@redhat.com> - 1.3.7-2
- fix error when ipv6 support isn't loaded in the kernel (#236888)

* Wed Jan 10 2007 Thomas Woerner <twoerner@redhat.com> 1.3.7-1.1
- fixed installation of secmark modules

* Tue Jan  9 2007 Thomas Woerner <twoerner@redhat.com> 1.3.7-1
- new verison 1.3.7
- iptc is not a public interface and therefore not installed anymore
- dropped upstream secmark patch

* Thu Sep 19 2006 Thomas Woerner <twoerner@redhat.com> 1.3.5-2
- added secmark iptables patches (#201573)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.3.5-1.2.1
- rebuild

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.3.5-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.3.5-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Feb  2 2006 Thomas Woerner <twoerner@redhat.com> 1.3.5-1
- new version 1.3.5
- fixed init script to set policy for raw tables, too (#179094)

* Tue Jan 24 2006 Thomas Woerner <twoerner@redhat.com> 1.3.4-3
- added important iptables header files to devel package

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Nov 25 2005 Thomas Woerner <twoerner@redhat.com> 1.3.4-2
- fix for plugin problem: link with "gcc -shared" instead of "ld -shared" and 
  replace "_init" with "__attribute((constructor)) my_init"

* Fri Nov 25 2005 Thomas Woerner <twoerner@redhat.com> 1.3.4-1.1
- rebuild due to unresolved symbols in shared libraries

* Fri Nov 18 2005 Thomas Woerner <twoerner@redhat.com> 1.3.4-1
- new version 1.3.4
- dropped free_opts patch (upstream fixed)
- made libipq PIC (#158623)
- additional configuration options for iptables startup script (#172929)
  Thanks to Jan Gruenwald for the patch
- spec file cleanup (dropped linux_header define and usage)

* Mon Jul 18 2005 Thomas Woerner <twoerner@redhat.com> 1.3.2-1
- new version 1.3.2 with additional patch for the misplaced free_opts call
  from Marcus Sundberg

* Wed May 11 2005 Thomas Woerner <twoerner@redhat.com> 1.3.1-1
- new version 1.3.1

* Fri Mar 18 2005 Thomas Woerner <twoerner@redhat.com> 1.3.0-2
- Remove unnecessary explicit kernel dep (#146142)
- Fixed out of bounds accesses (#131848): Thanks to Steve Grubb
  for the patch
- Adapted iptables-config to reference to modprobe.conf (#150143)
- Remove misleading message (#140154): Thanks to Ulrich Drepper
  for the patch

* Mon Feb 21 2005 Thomas Woerner <twoerner@redhat.com> 1.3.0-1
- new version 1.3.0

* Thu Nov 11 2004 Thomas Woerner <twoerner@redhat.com> 1.2.11-3.2
- fixed autoload problem in iptables and ip6tables (CAN-2004-0986)

* Fri Sep 17 2004 Thomas Woerner <twoerner@redhat.com> 1.2.11-3.1
- changed default behaviour for IPTABLES_STATUS_NUMERIC to "yes" (#129731)
- modified config file to match this change and un-commented variables with
  default values

* Thu Sep 16 2004 Thomas Woerner <twoerner@redhat.com> 1.2.11-3
- applied second part of cleanup patch from (#131848): thanks to Steve Grubb
  for the patch

* Wed Aug 25 2004 Thomas Woerner <twoerner@redhat.com> 1.2.11-2
- fixed free bug in iptables (#128322)

* Tue Jun 22 2004 Thomas Woerner <twoerner@redhat.com> 1.2.11-1
- new version 1.2.11

* Thu Jun 17 2004 Thomas Woerner <twoerner@redhat.com> 1.2.10-1
- new version 1.2.10

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 26 2004 Thomas Woerner <twoerner@redhat.com> 1.2.9-2.3
- fixed iptables-restore -c fault if there are no counters (#116421)

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sun Jan  25 2004 Dan Walsh <dwalsh@redhat.com> 1.2.9-1.2
- Close File descriptors to prevent SELinux error message

* Wed Jan  7 2004 Thomas Woerner <twoerner@redhat.com> 1.2.9-1.1
- rebuild

* Wed Dec 17 2003 Thomas Woerner <twoerner@redhat.com> 1.2.9-1
- vew version 1.2.9
- new config options in ipXtables-config:
  IPTABLES_MODULES_UNLOAD
- more documentation in ipXtables-config
- fix for netlink security issue in libipq (devel package)
- print fix for libipt_icmp (#109546)

* Thu Oct 23 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-13
- marked all messages in iptables init script for translation (#107462)
- enabled devel package (#105884, #106101)
- bumped build for fedora for libipt_recent.so (#106002)

* Tue Sep 23 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-12.1
- fixed lost udp port range in ip6tables-save (#104484)
- fixed non numeric multiport port output in ipXtables-savs

* Mon Sep 22 2003 Florian La Roche <Florian.LaRoche@redhat.de> 1.2.8-11
- do not link against -lnsl

* Wed Sep 17 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-10
- made variables in rmmod_r local

* Tue Jul 22 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-9
- fixed permission for init script

* Sat Jul 19 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-8
- fixed save when iptables file is missing and iptables-config permissions

* Tue Jul  8 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-7
- fixes for ip6tables: module unloading, setting policy only for existing 
  tables

* Thu Jul  3 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-6
- IPTABLES_SAVE_COUNTER defaults to no, now
- install config file in /etc/sysconfig
- exchange unload of ip_tables and ip_conntrack
- fixed start function

* Wed Jul  2 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-5
- new config option IPTABLES_SAVE_ON_RESTART
- init script: new status, save and restart
- fixes #44905, #65389, #80785, #82860, #91040, #91560 and #91374

* Mon Jun 30 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-4
- new config option IPTABLES_STATUS_NUMERIC
- cleared IPTABLES_MODULES in iptables-config

* Mon Jun 30 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-3
- new init scripts

* Sat Jun 28 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- remove check for very old kernel versions in init scripts
- sync up both init scripts and remove some further ugly things
- add some docu into rpm

* Thu Jun 26  2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-2
- rebuild

* Mon Jun 16 2003 Thomas Woerner <twoerner@redhat.com> 1.2.8-1
- update to 1.2.8

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Mon Jan 13 2003 Bill Nottingham <notting@redhat.com> 1.2.7a-1
- update to 1.2.7a
- add a plethora of bugfixes courtesy Michael Schwendt <mschewndt@yahoo.com>

* Fri Dec 13 2002 Elliot Lee <sopwith@redhat.com> 1.2.6a-3
- Fix multilib

* Wed Aug 07 2002 Karsten Hopp <karsten@redhat.de>
- fixed iptables and ip6tables initscript output, based on #70511
- check return status of all iptables calls, not just the last one
  in a 'for' loop.

* Mon Jul 29 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.6a-1
- 1.2.6a (bugfix release, #69747)

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Mar  4 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.5-3
- Add some fixes from CVS, fixing bug #60465

* Tue Feb 12 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.5-2
- Merge ip6tables improvements from Ian Prowell <iprowell@prowell.org>
  #59402
- Update URL (#59354)
- Use /sbin/chkconfig rather than chkconfig in %%postun script

* Fri Jan 11 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.5-1
- 1.2.5

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Nov  5 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.4-2
- Fix %%preun script

* Tue Oct 30 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.4-1
- Update to 1.2.4 (various fixes, including security fixes; among others:
  #42990, #50500, #53325, #54280)
- Fix init script (#31133)

* Mon Sep  3 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.3-1
- 1.2.3 (5 security fixes, some other fixes)
- Fix updating (#53032)

* Mon Aug 27 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.2-4
- Fix #50990
- Add some fixes from current CVS; should fix #52620

* Mon Jul 16 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.2-3
- Add some fixes from the current CVS tree; fixes #49154 and some IPv6
  issues

* Tue Jun 26 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.2-2
- Fix iptables-save reject-with (#45632), Patch from Michael Schwendt
  <mschwendt@yahoo.com>

* Tue May  8 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.2-1
- 1.2.2

* Wed Mar 21 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.2.1a, fixes #28412, #31136, #31460, #31133

* Thu Mar  1 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Yet another initscript fix (#30173)
- Fix the fixes; they fixed some issues but broke more important
  stuff :/ (#30176)

* Tue Feb 27 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix up initscript (#27962)
- Add fixes from CVS to iptables-{restore,save}, fixing #28412

* Fri Feb 09 2001 Karsten Hopp <karsten@redhat.de>
- create /etc/sysconfig/iptables mode 600 (same problem as #24245)

* Mon Feb 05 2001 Karsten Hopp <karsten@redhat.de>
- fix bugzilla #25986 (initscript not marked as config file)
- fix bugzilla #25962 (iptables-restore)
- mv chkconfig --del from postun to preun

* Thu Feb  1 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Fix check for ipchains

* Mon Jan 29 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Some fixes to init scripts

* Wed Jan 24 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Add some fixes from CVS, fixes among other things Bug #24732

* Wed Jan 17 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Add missing man pages, fix up init script (Bug #17676)

* Mon Jan 15 2001 Bill Nottingham <notting@redhat.com>
- add init script

* Mon Jan 15 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.2
- fix up ipv6 split
- add init script
- Move the plugins from /usr/lib/iptables to /lib/iptables.
  This needs to work before /usr is mounted...
- Use -O1 on alpha (compiler bug)

* Sat Jan  6 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.1.2
- Add IPv6 support (in separate package)

* Thu Aug 17 2000 Bill Nottingham <notting@redhat.com>
- build everywhere

* Tue Jul 25 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.1.1

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Tue Jun 27 2000 Preston Brown <pbrown@redhat.com>
- move iptables to /sbin.
- excludearch alpha for now, not building there because of compiler bug(?)

* Fri Jun  9 2000 Bill Nottingham <notting@redhat.com>
- don't obsolete ipchains either
- update to 1.1.0

* Mon Jun  4 2000 Bill Nottingham <notting@redhat.com>
- remove explicit kernel requirement

* Tue May  2 2000 Bernhard Rosenkränzer <bero@redhat.com>
- initial package
